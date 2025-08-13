import datetime
from os import getenv

from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode


class Refresh:
    """Gestion de la génération et vérification des tokens refresh."""

    def __init__(self) -> None:
        load_dotenv()
        self.security_token = getenv("ENCRYPT_TOKEN")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    def generate(self, user_id: int):
        """Génère un token refresh valide 7 jours."""
        payload = {
            "id": user_id,
            "type": "refresh",
            "exp": int((datetime.datetime.now() + datetime.timedelta(days=7)).timestamp())
        }

        token = encode(payload, self.security_token, algorithm="HS256")
        return token

    def verify(self, token: str):
        """Vérifie et décode un token refresh. Retourne l'ID utilisateur."""
        try:
            payload = decode(token, self.security_token, algorithms=["HS256"])
            return payload["id"]
        except ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            ) from exc
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            ) from exc
