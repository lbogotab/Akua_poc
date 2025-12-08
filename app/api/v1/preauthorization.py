from fastapi import APIRouter, HTTPException
from app.schemas.authorization import AuthorizationRequest
from app.infrastructure.akua_client import AkuaClient
from app.infrastructure.database import save_authorization

router = APIRouter(prefix="/preauthorization", tags=["preauthorization"])

@router.post("", summary="Crear una pre-autorización")
async def create_preauthorization(body: AuthorizationRequest):
    client = AkuaClient()
    body.intent = "pre-authorization"

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