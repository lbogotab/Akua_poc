from pydantic import BaseModel, Field, ConfigDict

class Card(BaseModel):
    number: str
    cvv: str
    expiration_month: str
    expiration_year: str
    holder_name: str


class Instrument(BaseModel):
    type: str = Field(default="CARD")
    card: Card


class Capture(BaseModel):
    mode: str = Field(default="AUTOMATIC")


class Installments(BaseModel):
    quantity: int = 1
    type: str = "issuer-financed"


class TransactionComplianceAmount(BaseModel):
    currency: str
    value: int


class TransactionCompliance(BaseModel):
    laws: list[str]
    taxable_amount: TransactionComplianceAmount


class ThreeDS(BaseModel):
    cavv: str | None = None
    version: str | None = None
    ds_transaction_id: str | None = None


class AuthorizationRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "intent": "authorization",
                "instrument": {
                    "type": "CARD",
                    "card": {
                        "number": "4111111111111111",
                        "cvv": "123",
                        "expiration_month": "12",
                        "expiration_year": "2030",
                        "holder_name": "Juan Pérez"
                    }
                },
                "merchant_id": "merchant_123",
                "id": "order_456",
                "entry_mode": "contactless",
                "order_type": "purchase",
                "initiator": "merchant",
                "capture": {
                    "mode": "AUTOMATIC"
                },
                "installments": {
                    "quantity": 1,
                    "type": "issuer-financed"
                },
                "three_ds": {
                    "cavv": "some_cavv_value",
                    "version": "2.1.0",
                    "ds_transaction_id": "ds_trans_id_789"
                },
                "eci": "05",
                "transaction_compliance": [
                    {
                        "laws": ["IVA"],
                        "taxable_amount": {
                            "currency": "COP",
                            "value": 10000
                        }
                    }
                ]
            }
        }
    )

    intent: str = Field(default="authorization")
    instrument: Instrument
    merchant_id: str
    id: str
    entry_mode: str = "contactless"
    order_type: str = "purchase"
    initiator: str = "merchant"
    capture: Capture | None = None
    installments: Installments | None = None
    three_ds: ThreeDS | None = None
    eci: str = "05"
    transaction_compliance: list[TransactionCompliance] | None = None