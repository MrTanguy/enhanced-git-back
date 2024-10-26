import logging

from api.auth import auth_router

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)


@app.get('/')
def hello():
    return {"message": "Hello World"}
