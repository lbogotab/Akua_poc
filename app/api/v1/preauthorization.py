from fastapi import APIRouter, HTTPException, Query
from app.schemas.authorization import AuthorizationRequest
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_authorization

router = APIRouter(prefix="/preauthorization", tags=["preauthorization"])

@router.post("", summary="Crear una pre-autorización")
async def create_preauthorization(
    amount_value: float = Query(default=100, description="Monto de la transacción en USD por restricción de Comercio"),
    holder_name: str = Query(default="ALEJANDRO BOGOTA", description="Nombre del titular (ej: ALEJANDRO BOGOTA)"),
    card_number: str = Query(default="5200000000000007", description="Número de tarjeta (ej: 5200000000000007)"),
    cvv: str = Query(default="123", description="Código CVV (ej: 123)"),
    expiration_month: str = Query(default="12", description="Mes de expiración (ej: 12)"),
    expiration_year: str = Query(default="26", description="Año de expiración (ej: 26)")
):
    client = AkuaClient()

    body = AuthorizationRequest(
        intent="pre-authorization",
        amount={"value": amount_value, "currency": "USD"},
        merchant_id="mer-d43nagkm4gl7c1b8dqhg",
        instrument={
            "type": "CARD",
            "card": {
                "number": card_number,
                "cvv": cvv,
                "expiration_month": expiration_month,
                "expiration_year": expiration_year,
                "holder_name": holder_name
            }
        },
        capture={"mode": "MANUAL", "capture_after": ""},
    )

    try:
        result = await client.create_authorization(body)
        akua = result.get("akua_response", {})

        save_authorization(
            merchant_id=body.merchant_id,
            authorization_id=body.id or "auto-generated",
            payment_id=akua.get("payment_id"),
            transaction_id=akua.get("transaction", {}).get("id"),
            status=akua.get("transaction", {}).get("status", "UNKNOWN"),
            raw_response=akua,
            auth_type="PRE_AUTHORIZATION",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result