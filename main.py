import logging

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from api.auth import auth_router 
from api.connection import connection_router
from api.user import user_router

app = FastAPI()

origins = [
    "https://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=connection_router, prefix="/connect")
app.include_router(router=user_router, prefix="/user")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)

@app.get('/')
def hello():
    return {"message": "Welcome to the Enhanced-git API"}
