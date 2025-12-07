from pydantic import BaseModel, Field, ConfigDict

class CheckoutCard(BaseModel):
    number: str
    cvv: str
    exp_month: str
    exp_year: str
    holder_name: str


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ORD-12345",
                "amount": 150000,
                "currency": "COP",
                "card": {
                    "number": "5191872272166422",
                    "cvv": "917",
                    "exp_month": "12",
                    "exp_year": "26",
                    "holder_name": "ALEJANDRO BOGOTA"
                },
                "capture_mode": "AUTOMATIC"
            }
        }
    )

    order_id: str = Field(..., description="Identificador interno de la orden del e-commerce")
    amount: int = Field(..., description="Monto total de la orden")
    currency: str = Field(..., description="Moneda")
    card: CheckoutCard
    capture_mode: str = Field(default="AUTOMATIC", description="AUTOMATIC o MANUAL (preautorización)")