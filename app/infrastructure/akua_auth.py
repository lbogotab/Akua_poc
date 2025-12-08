import requests
from app.config import settings

class AkuaAuth:
    TOKEN_URL = f"{settings.akua_base_url}/oauth/token"

    @staticmethod
    def get_access_token():
        payload = {
            "grant_type": "client_credentials",
            "audience": settings.akua_base_url,
            "client_id": settings.akua_client_id,
            "client_secret": settings.akua_client_secret,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(AkuaAuth.TOKEN_URL, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error obteniendo token Akua: {response.text}")

        data = response.json()
        return data["access_token"], data.get("expires_in", 0)