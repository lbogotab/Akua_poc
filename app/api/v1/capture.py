from fastapi import APIRouter, HTTPException, Query
from app.schemas.capture import CaptureRequest
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_capture

router = APIRouter(prefix="/capture", tags=["capture"])

@router.post("/{payment_id}", summary="Capturar un pago")
async def capture_payment(
    payment_id: str,
    body: CaptureRequest,
    value: float | None = Query(
        default=None,
        description="Monto parcial a capturar. Si se omite, se captura el monto completo",
    ),
    currency: str | None = Query(
        default=None,
        description="Moneda del monto a capturar. Si se omite, se usa la moneda del pago",
    ),
):
    client = AkuaClient()

    if value is not None or currency is not None:
        if body.amount is None:
            body.amount = {
                "value": value if value is not None else 0,
                "currency": currency if currency is not None else "USD",
            }
        else:
            if value is not None:
                body.amount.value = value
            if currency is not None:
                body.amount.currency = currency

    try:
        result = await client.capture_payment(payment_id, body)
        akua = result.get("akua_response", {})

        save_capture(
            payment_id=akua.get("payment_id"),
            transaction_id=akua.get("transaction", {}).get("id"),
            amount=str(akua.get("transaction", {}).get("amount")) if akua.get("transaction") else None,
            status=akua.get("transaction", {}).get("status", "UNKNOWN"),
            raw_response=akua,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result