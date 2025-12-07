import uuid
import httpx

from app.config import settings
from app.schemas.authorization import AuthorizationRequest
from app.schemas.cancel import CancelRequest
from app.schemas.capture import CaptureRequest
from app.schemas.refund import RefundRequest


class AkuaClient:
    """
    Cliente de Akua con 2 modos:
    - MOCK: devuelve respuesta simulada
    - REAL: hace POST a /v1/authorizations usando AKUA_BASE_URL y AKUA_ACCESS_TOKEN
    """

    def __init__(self) -> None:
        self.mode = (settings.akua_mode or "MOCK").upper()
        self.base_url = settings.akua_base_url
        self.access_token = settings.akua_access_token

    async def create_authorization(self, payload: AuthorizationRequest) -> dict:
        if self.mode == "MOCK":
            return self._mock_authorization(payload)
        else:
            return await self._real_authorization(payload)

    # MODO MOCK
    def _mock_authorization(self, payload: AuthorizationRequest) -> dict:
        instrument_id = f"ins-{uuid.uuid4().hex[:20]}"
        payment_id = f"pay-{uuid.uuid4().hex[:20]}"
        transaction_id = f"trx-{uuid.uuid4().hex[:20]}"
        risk_id = f"eva-{uuid.uuid4().hex[:20]}"

        mock_response = {
            "instrument_id": instrument_id,
            "payment_id": payment_id,
            "response_code": "00",
            "response_code_description": "Approved or completed successfully",
            "transaction": {
                "amount": "321.23",
                "id": transaction_id,
                "network_data": {
                    "approval_code": "772886",
                    "banknet_reference_number": "000UNB",
                    "financial_network_code": "MCC",
                    "response_code": "00",
                    "response_code_description": "Approved or completed successfully",
                    "settlement_date": "0211",
                    "system_trace_audit_number": "621157",
                    "transmission_date_time": "0211201021",
                    "merchant_advice_code": "01",
                    "merchant_advice_description": "Update card details and retry",
                    "merchant_advice_action": "UPDATE_AND_RETRY"
                },
                "risk_id": risk_id,
                "status": "APPROVED",
                "status_detail": "SUCCESS",
                "type": "AUTHORIZATION"
            }
        }

        return {
            "mode": "MOCK",
            "echo_request": payload.model_dump(),
            "akua_response": mock_response,
        }

    # MODO REAL
    async def _real_authorization(self, payload: AuthorizationRequest) -> dict:
        if not self.access_token:
            raise RuntimeError(
                "AKUA_MODE=REAL pero AKUA_ACCESS_TOKEN no está configurado"
            )

        url = f"{self.base_url.rstrip('/')}/v1/authorizations"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            # Opcional
            "Idempotency-Key": payload.id,
            "authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload.model_dump(), headers=headers)

        response.raise_for_status()
        return {
            "mode": "REAL",
            "akua_response": response.json(),
        }
    
    ### Cancelamiento de pagos ###

    async def cancel_payment(self, payment_id: str, payload: CancelRequest) -> dict:
        if self.mode == "MOCK":
            return self._mock_cancel(payment_id, payload)
        else:
            return await self._real_cancel(payment_id, payload)

    # MOCK
    def _mock_cancel(self, payment_id: str, payload: CancelRequest) -> dict:
        trx_id = f"trx-{uuid.uuid4().hex[:20]}"

        return {
            "mode": "MOCK",
            "payment": {
                "id": payment_id,
                "transaction": {
                    "amount": 25.25,
                    "id": trx_id,
                    "status": "APPROVED",
                    "status_detail": "SUCCESS",
                    "network_data": {
                        "settlement_date": "0211",
                        "system_trace_audit_number": "621157",
                        "transmission_date_time": "0211201021"
                    },
                    "system_trace_audit_number": "517127",
                    "transmission_date_time": "0121183517",
                    "type": "CANCEL"
                }
            }
        }

    # REAL
    async def _real_cancel(self, payment_id: str, payload: CancelRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL pero AKUA_ACCESS_TOKEN no está configurado")

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
        MODO MOCK: respuesta simulada
        MODO REAL: llama a Akua /v1/payments/{payment_id}/refund
        """
        if self.mode == "MOCK":
            return self._mock_refund(payment_id, payload)
        else:
            return await self._real_refund(payment_id, payload)

    # MOCK
    def _mock_refund(self, payment_id: str, payload: RefundRequest) -> dict:
        trx_id = f"trx-{uuid.uuid4().hex[:20]}"

        return {
            "mode": "MOCK",
            "payment": {
                "id": payment_id,
                "transaction": {
                    "amount": payload.amount.value,
                    "authorization_code": "744019",
                    "id": trx_id,
                    "status": "APPROVED",
                    "status_detail": "SUCCESS",
                    "network_data": {
                        "approval_code": "772886",
                        "settlement_date": "0211",
                        "system_trace_audit_number": "621157",
                        "transmission_date_time": "0211201021"
                    },
                    "type": "REFUND"
                }
            }
        }

    # REAL
    async def _real_refund(self, payment_id: str, payload: RefundRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL pero AKUA_ACCESS_TOKEN no está configurado")

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
        Captura de un pago con captura manual.
        MODO MOCK: respuesta simulada.
        MODO REAL: llama a Akua /v1/payments/{payment_id}/captures.
        """
        if self.mode == "MOCK":
            return self._mock_capture(payment_id, payload)
        else:
            return await self._real_capture(payment_id, payload)

    # MOCK
    def _mock_capture(self, payment_id: str, payload: CaptureRequest) -> dict:
        trx_id = f"trx-{uuid.uuid4().hex[:20]}"

        # Simulación del monto capturado
        amount_value = payload.amount.value if payload.amount else 100
        amount_currency = (
            payload.amount.currency if payload.amount else "USD"
        )

        return {
            "mode": "MOCK",
            "payment": {
                "id": payment_id,
                "transaction": {
                    "amount": amount_value,
                    "id": trx_id,
                    "status": "PENDING",
                    "type": "CAPTURE",
                }
            }
        }

    # REAL
    async def _real_capture(self, payment_id: str, payload: CaptureRequest) -> dict:
        if not self.access_token:
            raise RuntimeError("AKUA_MODE=REAL pero AKUA_ACCESS_TOKEN no está configurado")

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