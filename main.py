import logging

from api.auth import auth_router

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth")

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
