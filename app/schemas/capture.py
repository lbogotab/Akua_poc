from pydantic import BaseModel, ConfigDict

class CaptureAmount(BaseModel):
    value: int | float
    currency: str


class CaptureRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
            }
        },
    )

    amount: CaptureAmount | None = None