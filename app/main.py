from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.infrastructure.database import init_db
from .api.v1.hello import router as hello_router
from .api.v1.authorization import router as authorization_router
from .api.v1.cancel import router as cancel_router
from .api.v1.refund import router as refund_router
from .api.v1.capture import router as capture_router
from .api.v1.preauthorization import router as preauthorization_router
from .api.v1.checkout import router as checkout_router
from .api.v1.token_test import router as token_test_router
from .api.v1.organization import router as organization_router
from .api.v1.merchants import router as merchants_router

def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="Akua PoC",
        version="0.1.0",
        description=(
            "PoC de integración con Akua\n\n"
            "- Flujos básicos de pagos: autorización, pre-autorización, captura, cancelación y reembolso\n"
            "- Endpoint de ejemplo de e-commerce (`/v1/ecommerce/checkout`) que:\n"
            "  1) Recibe una orden y datos de tarjeta\n"
            "  2) Mapea al esquema de autorización de Akua\n"
            "  3) Llama a Akua (MOCK o REAL según AKUA_MODE)\n"
            "  4) Guarda el resultado en SQLite\n"
        ),
    )

    @app.get("/", tags=["root"])
    async def root():
        return {"message": "Akua PoC - Hola Mundo"}

    app.include_router(hello_router, prefix="/v1")
    app.include_router(authorization_router, prefix="/v1")
    app.include_router(cancel_router, prefix="/v1")
    app.include_router(refund_router, prefix="/v1")
    app.include_router(capture_router, prefix="/v1")
    app.include_router(preauthorization_router, prefix="/v1")
    app.include_router(checkout_router, prefix="/v1")
    app.include_router(token_test_router, prefix="/v1")
    app.include_router(organization_router, prefix="/v1")
    app.include_router(merchants_router, prefix="/v1")

    return app

app = create_app()