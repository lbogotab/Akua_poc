import requests
from fastapi import APIRouter, HTTPException
from app.config import settings

router = APIRouter(prefix="/akua", tags=["akua-token"])


@router.get("/token/test", summary="Obtener Credenciales Akua válidas")
def test_akua_token():
    """
    Este endpoint valida que el Client ID y Client Secret permitan obtener
    un access_token real desde Akua.
    """

    if not settings.akua_client_id or not settings.akua_client_secret:
        raise HTTPException(
            status_code=400,
            detail="AKUA_CLIENT_ID o AKUA_CLIENT_SECRET no están configurados en .env"
        )

    url = f"{settings.akua_base_url}/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "audience": settings.akua_base_url,
        "client_id": settings.akua_client_id,
        "client_secret": settings.akua_client_secret
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando con Akua: {e}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()

    return {
        "status": "ok",
        "token_prefix": data["access_token"][:20] + "...",
        "expires_in": data.get("expires_in"),
        "token_type": data.get("token_type")
    }