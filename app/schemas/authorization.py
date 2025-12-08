from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class Amount(BaseModel):
    value: float
    currency: str

class Card(BaseModel):
    number: str
    cvv: str
    expiration_month: str
    expiration_year: str
    holder_name: str


class Instrument(BaseModel):
    type: str
    card: Card


class Capture(BaseModel):
    mode: str = Field(default="AUTOMATIC")
    capture_after: Optional[str] = None


class Installments(BaseModel):
    quantity: int
    type: str


class ThreeDS(BaseModel):
    cavv: str
    version: str
    ds_transaction_id: str


class TaxableAmount(BaseModel):
    currency: str
    value: float


class TransactionCompliance(BaseModel):
    laws: List[str]
    taxable_amount: TaxableAmount


class AuthorizationRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "amount": {
                    "value": 60.25,
                    "currency": "USD"
                },
                "intent": "authorization",
                "instrument": {
                    "card": {
                        "number": "5186170070001108",
                        "cvv": "917",
                        "expiration_month": "12",
                        "expiration_year": "25",
                        "holder_name": "ALEJO BOGOTA"
                    },
                    "type": "CARD"
                },
                "merchant_id": "mer-d43nagkm4gl7c1b8dqhg",
                "capture": {
                    "mode": "MANUAL",
                    "capture_after": ""
                }
            }
        }
    )

    intent: str
    amount: Amount
    instrument: Instrument
    merchant_id: str

    id: Optional[str] = None
    entry_mode: Optional[str] = None
    order_type: Optional[str] = None
    initiator: Optional[str] = None
    capture: Capture
    installments: Optional[Installments] = None
    three_ds: Optional[ThreeDS] = None
    eci: Optional[str] = None
    transaction_compliance: Optional[List[TransactionCompliance]] = None