from fastapi import APIRouter, HTTPException
from app.schemas.capture import CaptureRequest
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/capture", tags=["capture"])

@router.post("/{payment_id}", summary="Capturar un pago")
async def capture_payment(payment_id: str, body: CaptureRequest):
    client = AkuaClient()

    try:
        result = await client.capture_payment(payment_id, body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result