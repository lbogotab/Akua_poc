from pydantic import BaseModel, ConfigDict

class CaptureAmount(BaseModel):
    value: int | float
    currency: str


class CaptureRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                # Si se incluye amount, se hace una captura parcial por ese monto
                # Si se omite amount, Akua captura el monto total pendiente del pago
                "amount": {
                    "value": 60.25,
                    "currency": "USD"
                }
            }
        },
    )

    amount: CaptureAmount | None = None