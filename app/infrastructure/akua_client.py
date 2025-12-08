import uuid
import httpx

from app.config import settings
from app.schemas.authorization import AuthorizationRequest
from app.schemas.cancel import CancelRequest
from app.schemas.capture import CaptureRequest
from app.schemas.refund import RefundRequest
from app.infrastructure.akua_auth import AkuaAuth
class AkuaClient:
    """
    Cliente de Akua en modo SandBox usando AKUA_BASE_URL y AKUA_ACCESS_TOKEN
    """

    def __init__(self) -> None:
        self.base_url = (settings.akua_base_url or "").rstrip("/")

        if settings.akua_access_token:
            self.access_token = settings.akua_access_token

        elif settings.akua_client_id and settings.akua_client_secret:
            token, _ = AkuaAuth.get_access_token()
            self.access_token = token

        else:
            self.access_token = None

    async def create_authorization(self, payload: AuthorizationRequest) -> dict:
        if not getattr(payload, "id", None):
            payload.id = f"auto-{uuid.uuid4().hex[:12]}"
        return await self._real_authorization(payload)

    async def _real_authorization(self, payload: AuthorizationRequest) -> dict:
        if not self.access_token:
            raise RuntimeError(
                "AKUA_MODE=REAL requiere AKUA_ACCESS_TOKEN o (AKUA_CLIENT_ID + AKUA_CLIENT_SECRET)"
            )

        url = f"{self.base_url.rstrip('/')}/v1/authorizations"

        json_payload = payload.model_dump(exclude_none=True)
        idempotency_key = f"{payload.id}-{uuid.uuid4()}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "Idempotency-Key": idempotency_key,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=json_payload, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(
                f"ERROR desde Akua Authorization:\n"
                f"- Status: {response.status_code}\n"
                f"- URL: {url}\n"
                f"- Request JSON: {json_payload}\n"
                f"- Response Body: {response.text}"
            )

        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }
    
    ### Cancelamiento de pagos ###

    async def cancel_payment(self, payment_id: str, payload: CancelRequest) -> dict:
        return await self._real_cancel(payment_id, payload)

    async def _real_cancel(self, payment_id: str, payload: CancelRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL requiere AKUA_ACCESS_TOKEN o (AKUA_CLIENT_ID + AKUA_CLIENT_SECRET)")

        url = f"{self.base_url.rstrip('/')}/v1/payments/{payment_id}/cancel"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Idempotency-Key": f"cancel-{payment_id}",
            "authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload.model_dump(), headers=headers)
        
        response.raise_for_status()
        return {"mode": "REAL", "akua_response": response.json()}
    
    ### Reembolso de pagos ###

    async def refund_payment(self, payment_id: str, payload: RefundRequest) -> dict:
        """
        Reembolso de un pago
        Llama Akua /v1/payments/{payment_id}/refund
        """
        return await self._real_refund(payment_id, payload)

    async def _real_refund(self, payment_id: str, payload: RefundRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL requiere AKUA_ACCESS_TOKEN o (AKUA_CLIENT_ID + AKUA_CLIENT_SECRET)")

        url = f"{self.base_url.rstrip('/')}/v1/payments/{payment_id}/refund"
        idem_key = f"refund-{payment_id}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Idempotency-Key": idem_key,
            "authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload.model_dump(), headers=headers)

        response.raise_for_status()
        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }
    
    ### Captura de pagos ###
    
    async def capture_payment(self, payment_id: str, payload: CaptureRequest) -> dict:
        """
        Captura de un pago con captura manual
        Llama a Akua /v1/payments/{payment_id}/captures
        """
        return await self._real_capture(payment_id, payload)

    async def _real_capture(self, payment_id: str, payload: CaptureRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL requiere AKUA_ACCESS_TOKEN o (AKUA_CLIENT_ID + AKUA_CLIENT_SECRET)")

        url = f"{self.base_url.rstrip('/')}/v1/payments/{payment_id}/captures"

        if payload.amount:
            idem_key = f"capture-{payment_id}"
        else:
            idem_key = f"capture-{payment_id}-full"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Idempotency-Key": idem_key,
            "authorization": f"Bearer {self.access_token}",
        }

        json_body = payload.model_dump(exclude_none=True)

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=json_body, headers=headers)

        response.raise_for_status()
        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }

    async def list_organizations(self) -> dict:
        """
        Obtiene el listado de organizaciones desde Akua

        Llama al endpoint /v1/organizations de Akua
        """
        return await self._real_list_organizations()

    async def _real_list_organizations(self) -> dict:
        if not self.access_token:
            raise RuntimeError(
                "AKUA_MODE=REAL requiere un access token de Akua "
                "o configuración de client_credentials"
            )

        url = f"{self.base_url.rstrip('/')}/v1/organizations"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(
                "ERROR desde Akua Organizations:\n"
                f"- Status: {response.status_code}\n"
                f"- URL: {url}\n"
                f"- Response Body: {response.text}"
            )

        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }

    async def list_merchants(self, organization_id: str, page: int = 1, page_size: int = 20) -> dict:
        """
        Lista comerciantes (merchants) asociados a una organización en Akua
        Llama a /v1/merchants usando filtros de query
        """
        return await self._real_list_merchants(organization_id, page, page_size)

    async def _real_list_merchants(self, organization_id: str, page: int, page_size: int) -> dict:
        if not self.access_token:
            raise RuntimeError(
                "AKUA_MODE=REAL requiere AKUA_ACCESS_TOKEN o (AKUA_CLIENT_ID + AKUA_CLIENT_SECRET)"
            )

        url = (
            f"{self.base_url.rstrip('/')}/v1/merchants"
            f"?page={page}&page_size={page_size}"
            f"&sort=created_at:asc&organization_id={organization_id}"
        )

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(
                "ERROR desde Akua Merchants:\n"
                f"- Status: {response.status_code}\n"
                f"- URL: {url}\n"
                f"- Response Body: {response.text}"
            )

        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }