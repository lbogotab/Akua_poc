from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Healthcheck"])


@router.get("", summary="Servicio de healthcheck del API", status_code=200)
async def health_check():
    return {
        "status": "ok",
        "message": "Servicio operativo",
        "component": "Akua Integration PoC"
    }