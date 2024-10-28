import logging

from api.auth import auth_router

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

import ssl

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth")

origins = [
    "http://localhost:3000",   # Autoriser React en développement
    "https://localhost:3000"   # Autoriser React en HTTPS
]

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Autoriser les origines spécifiées
    allow_credentials=True,        # Permettre les cookies
    allow_methods=["*"],           # Autoriser toutes les méthodes HTTP
    allow_headers=["*"]            # Autoriser tous les en-têtes
)

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('./cert/cert.pem', keyfile='./cert/key.pem')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)


@app.get('/')
def hello():
    return {"message": "Hello World"}
