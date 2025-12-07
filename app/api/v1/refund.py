from fastapi import APIRouter, HTTPException
from app.schemas.refund import RefundRequest
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/refund", tags=["refund"])


@router.post("/{payment_id}", summary="Reembolsar un pago")
async def refund_payment(payment_id: str, body: RefundRequest):
    client = AkuaClient()

    try:
        result = await client.refund_payment(payment_id, body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result