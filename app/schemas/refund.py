from pydantic import BaseModel, ConfigDict


class RefundAmount(BaseModel):
    value: int | float
    currency: str


class RefundRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "amount": {
                    "value": 60.25,
                    "currency": "USD"
                }
            }
        }
    )

    amount: RefundAmount