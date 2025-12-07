from fastapi import APIRouter, HTTPException
from app.schemas.authorization import AuthorizationRequest, Capture
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/preauthorization", tags=["preauthorization"])

@router.post("", summary="Crear una pre-autorización con capture.mode=MANUAL obligatorio")
async def create_preauthorization(body: AuthorizationRequest):
    client = AkuaClient()

    if body.capture is None:
        body.capture = Capture(mode="MANUAL")
    else:
        body.capture.mode = "MANUAL"

    try:
        result = await client.create_authorization(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result