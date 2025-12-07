from fastapi import APIRouter, HTTPException
from app.schemas.checkout import CheckoutRequest, CheckoutCard
from app.schemas.authorization import AuthorizationRequest, Instrument, Card, Capture, Installments
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_payment
from app.config import settings

router = APIRouter(prefix="/ecommerce", tags=["ecommerce"])


@router.post("/checkout", summary="Simulación de pago de e-commerce usando Akua")
async def ecommerce_checkout(body: CheckoutRequest):
    """
    Flujo de ejemplo:
    - Recibe datos de la orden y tarjeta (Simulación Cliente)
    - Construye AuthorizationRequest (Mapeo interno para campos Akua)
    - Llama a Akua (Petición a Akua)
    - Guarda el resultado en SQLite (Almacenamiento local)
    """

    if not settings.akua_merchant_id:
        raise HTTPException(
            status_code=500,
            detail="AKUA_MERCHANT_ID no está configurado en las variables de entorno",
        )

    client = AkuaClient()

    # 1. Mapear CheckoutRequest
    auth_payload = AuthorizationRequest(
        intent="authorization",
        merchant_id=settings.akua_merchant_id,
        id=f"order-{body.order_id}",
        instrument=Instrument(
            type="CARD",
            card=Card(
                number=body.card.number,
                cvv=body.card.cvv,
                expiration_month=body.card.exp_month,
                expiration_year=body.card.exp_year,
                holder_name=body.card.holder_name,
            ),
        ),
        entry_mode="ecommerce",
        order_type="purchase",
        initiator="cardholder",
        capture=Capture(mode=body.capture_mode),
        installments=Installments(quantity=1, type="issuer-financed"),
        eci="05",
        transaction_compliance=[],
    )

    # 2. Llamar a Akua (MOCK/REAL)
    try:
        akua_result = await client.create_authorization(auth_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Akua: {e}")

    akua_body = akua_result["akua_response"]

    # 3. Extraer datos relevantes
    payment_id = akua_body.get("payment_id")
    transaction = akua_body.get("transaction", {})
    transaction_id = transaction.get("id")
    status = transaction.get("status")

    if not payment_id or not transaction_id or not status:
        raise HTTPException(
            status_code=502,
            detail="Respuesta de Akua incompleta. No se pudo registrar el pago.",
        )

    # 4. Guardar en SQLite
    save_payment(
        order_id=body.order_id,
        payment_id=payment_id,
        transaction_id=transaction_id,
        status=status,
        raw_response=akua_body,
    )

    # 5. Responder al e-commerce
    return {
        "order_id": body.order_id,
        "payment_id": payment_id,
        "transaction_id": transaction_id,
        "status": status,
        "mode": akua_result.get("mode", "UNKNOWN"),
    }