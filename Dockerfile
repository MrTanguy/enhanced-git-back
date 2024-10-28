# Utiliser une image de base légère avec Python 3.12
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application dans le conteneur
COPY . .
COPY cert ./cert

# Exposer le port 8000 pour FastAPI
EXPOSE 8000

# Lancer l'application avec Uvicorn en mode SSL
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--ssl-keyfile", "./cert/cert.key", "--ssl-certfile", "./cert/cert.crt"]
