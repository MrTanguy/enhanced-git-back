import datetime
import logging
from dotenv import load_dotenv
from os import getenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode

class Refresh:
    def __init__(self) -> None:
        load_dotenv()
        self.SECURITY_TOKEN = getenv("REFRESH_SECRET_TOKEN")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    def generate(self, _id: int):
        payload = {
            "id": _id,
            "type": "refresh",
            "exp": datetime.datetime.now() - datetime.timedelta(days=7)
        }

        token = encode(payload, self.SECURITY_TOKEN, algorithm="HS256")
        return token
    
    def verify(self, token: str):
        try:
            payload = decode(token, self.SECURITY_TOKEN, algorithms=["HS256"])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )