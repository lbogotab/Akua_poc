import os
from dataclasses import dataclass

@dataclass
class Settings:
    akua_mode: str = os.getenv("AKUA_MODE", "MOCK")  # MOCK o REAL
    akua_base_url: str = os.getenv("AKUA_BASE_URL", "https://sandbox.akua.la")
    akua_access_token: str | None = os.getenv("AKUA_ACCESS_TOKEN")
    akua_merchant_id: str | None = os.getenv("AKUA_MERCHANT_ID")

settings = Settings()