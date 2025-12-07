from fastapi import APIRouter, HTTPException
from app.schemas.authorization import AuthorizationRequest
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/authorization", tags=["authorization"])

# https://docs.akua.la/reference/authorize

@router.post("", summary="Crear autorización")
async def create_authorization_endpoint(body: AuthorizationRequest):

    client = AkuaClient()

    try:
        result = await client.create_authorization(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result