import logging

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from api.auth import auth_router 
from api.connection import connection_router
from api.user import user_router
from api.portfolio import portfolio_router
from services.db.db import DB

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
app.include_router(router=portfolio_router, prefix="/portfolio")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)

@app.get('/')
def hello():
    return {"message": "Welcome to the Enhanced-git API"}

@app.get('/bdd')
def bdd():
    DB().create_bdd()
