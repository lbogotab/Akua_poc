from pydantic import BaseModel, Field, ConfigDict


class BaseAmount(BaseModel):
    currency: str
    value: int


class Tax(BaseModel):
    type: str
    percentage: float
    base_amount: BaseAmount
    laws: list[str]


class CancelRequest(BaseModel):
    model_config = ConfigDict(
    extra="ignore",
    json_schema_extra={
        "example": {
            "taxes": [
                {
                    "type": "IVA",
                    "percentage": 19,
                    "base_amount": {
                        "currency": "COP",
                        "value": 100000
                    },
                    "laws": ["4x1000"]
                }
            ]
        }
    }
)

    taxes: list[Tax] | None = None