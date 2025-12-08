from fastapi import APIRouter, HTTPException
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/v1", tags=["Organizations"])

@router.get("/organizations")
async def list_organizations():
    client = AkuaClient()
    """
    Lista las organizaciones configuradas en Akua para el token actual.

    - En modo MOCK devuelve datos de ejemplo.
    - En modo REAL consulta a Akua y devuelve el JSON tal cual.
    """
    try:
        return await client.list_organizations()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error consultando organizaciones en Akua: {e}",
        )