import datetime
from os import getenv
from typing import Annotated

from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode


class Bearer:
    """Handles Bearer token generation and verification."""

    def __init__(self) -> None:
        load_dotenv()
        self.security_token = getenv("BEARER_SECRET_TOKEN")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    def generate(self, user_id: int):
        """Generate a JWT Bearer token with 1 hour expiration."""
        payload = {
            "id": user_id,
            "type": "bearer",
            "exp": datetime.datetime.now() + datetime.timedelta(hours=1)
        }

        token = encode(payload, self.security_token, algorithm="HS256")
        return token

    def verify(self, token: str):
        """Decode and verify a JWT Bearer token."""
        try:
            payload = decode(token, self.security_token, algorithms=["HS256"])
            return payload
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

    def get_user_id(self, token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="auth/token"))]):
        """Extract the user ID from a validated JWT Bearer token."""
        payload = self.verify(token)
        return payload.get("id")
