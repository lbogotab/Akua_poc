from fastapi import APIRouter, HTTPException
from app.schemas.cancel import CancelRequest
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/cancel", tags=["cancel"])

# https://docs.akua.la/reference/authorize-cancel

@router.post("/{payment_id}", summary="Cancelar un pago")
async def cancel_payment(payment_id: str, body: CancelRequest):
    client = AkuaClient()
    try:
        result = await client.cancel_payment(payment_id, body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return result