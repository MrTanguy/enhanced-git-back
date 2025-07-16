# Utiliser une image de base légère avec Python 3.12
FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application dans le conteneur
COPY . .

# Exposer le port 8000 pour FastAPI
EXPOSE 8000

# Lancer l'application avec Uvicorn en mode SSL
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
