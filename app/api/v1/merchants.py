from fastapi import APIRouter, HTTPException, Query
from app.infrastructure.akua_client import AkuaClient

router = APIRouter(prefix="/v1", tags=["Merchants"])

@router.get(
    "/merchants",
    summary="Listar comercios (merchants) desde Akua",
    description=(
        "Lista comercios asociados a una organización en Akua Sandbox"
    ),
)
async def list_merchants(
    organization_id: str = Query(..., description="ID de la organización en Akua"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
):

    akua_client = AkuaClient()

    try:
        return await akua_client.list_merchants(
            organization_id=organization_id,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error consultando merchants en Akua: {e}",
        )