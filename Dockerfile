# Utilise une image Python légère
FROM python:3.10-slim

# Définit le répertoire de travail
WORKDIR /app

RUN apt-get update && apt-get install -y git

# Copie les dépendances et installe-les
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code du projet
COPY . .

# Expose le port de l'API
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "scripts.api_sentra:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
