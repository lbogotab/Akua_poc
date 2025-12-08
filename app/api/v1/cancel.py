from fastapi import APIRouter, HTTPException
from app.schemas.cancel import CancelRequest
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_cancellation

router = APIRouter(prefix="/cancel", tags=["cancel"])

# https://docs.akua.la/reference/authorize-cancel

@router.post("/{payment_id}", summary="Cancelar un pago")
async def cancel_payment(payment_id: str, body: CancelRequest):
    client = AkuaClient()
    try:
        result = await client.cancel_payment(payment_id, body)
        akua = result.get("akua_response", {})

        save_cancellation(
            payment_id=akua.get("payment_id"),
            transaction_id=akua.get("transaction", {}).get("id"),
            status=akua.get("transaction", {}).get("status", "UNKNOWN"),
            raw_response=akua,
        )

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return result