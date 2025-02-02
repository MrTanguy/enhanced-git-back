import logging

from api.auth import auth_router 
from api.connection import connection_router
from api.user import user_router

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=connection_router, prefix="/connect")
app.include_router(router=user_router, prefix="/user")

origins = [
    "https://localhost:5173"   # Autoriser React en HTTPS
]

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Autoriser les origines spécifiées
    allow_credentials=True,        # Permettre les cookies
    allow_methods=["*"],           # Autoriser toutes les méthodes HTTP
    allow_headers=["*"]            # Autoriser tous les en-têtes
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)


@app.get('/')
def hello():
    return {"message": "Welcome to the Enhanced-git API"}
