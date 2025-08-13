import datetime
from os import getenv

from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode


class Refresh:
    """Handles Refresh token generation and verification."""

    def __init__(self) -> None:
        load_dotenv()
        self.security_token = getenv("ENCRYPT_TOKEN")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    def generate(self, user_id: int):
        """Generate a Refresh token with 7 days expiration."""
        payload = {
            "id": user_id,
            "type": "refresh",
            "exp": int((datetime.datetime.now() + datetime.timedelta(days=7)).timestamp())
        }

        token = encode(payload, self.security_token, algorithm="HS256")
        return token

    def verify(self, token: str):
        """Decode and verify a Refresh token."""
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
