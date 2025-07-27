# Utiliser une image de base Python
FROM python:3.11-slim

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y curl build-essential git

# Installer les dépendances Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Lint auto avec Ruff
RUN pip install ruff

# Pour support YAML dans prompt_pool_loader
RUN pip install pyyaml

# Copier le projet
COPY . .

# Lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

RUN pip install openai
