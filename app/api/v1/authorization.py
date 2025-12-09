from fastapi import APIRouter, HTTPException, Query
from app.schemas.authorization import AuthorizationRequest
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_authorization

router = APIRouter(prefix="/authorization", tags=["authorization"])

# https://docs.akua.la/reference/authorize

@router.post("", summary="Crear autorización")
async def create_authorization_endpoint(
    body: AuthorizationRequest,
    amount: float | None = Query(default=100, description="Monto de la transacción (en USD por restricción de Comercio)"),
    intent: str | None = Query(default="authorization", description="authorization o pre-authorization"),
    holder_name: str | None = Query(default="ALEJANDRO BOGOTA", description="Nombre del tarjetahabiente (Ejp: ALEJANDRO BOGOTA)"),
    card_number: str | None = Query(default="5200000000000007", description="Número de tarjeta (Ejp: 5200000000000007)"),
    card_cvv: str | None = Query(default="123", description="CVV (Ejp: 123)"),
    card_exp_month: str | None = Query(default="12", description="Mes expiración (Ejp: 12)"),
    card_exp_year: str | None = Query(default="26", description="Año expiración (Ejp: 26)"),
):

    client = AkuaClient()

    if amount is not None and body.amount is not None:
        body.amount.value = amount

    if intent is not None:
        body.intent = intent

    if holder_name is not None and body.instrument and body.instrument.card:
        body.instrument.card.holder_name = holder_name

    if card_number is not None and body.instrument and body.instrument.card:
        body.instrument.card.number = card_number

    if card_cvv is not None and body.instrument and body.instrument.card:
        body.instrument.card.cvv = card_cvv

    if card_exp_month is not None and body.instrument and body.instrument.card:
        body.instrument.card.expiration_month = card_exp_month

    if card_exp_year is not None and body.instrument and body.instrument.card:
        body.instrument.card.expiration_year = card_exp_year

    # Currency siempre USD
    if body.amount is not None:
        body.amount.currency = "USD"

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
            auth_type="AUTHORIZATION"
        )
        
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result