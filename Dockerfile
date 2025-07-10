FROM python:3.10

WORKDIR /app

# Copier uniquement ce qu’il faut d’abord pour build plus vite
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code/app une fois les dépendances installées
COPY . .

# Crée les dossiers critiques si absents (au démarrage, ce sera monté via volumes)
RUN mkdir -p /app/memory /app/logs /app/projects

CMD ["uvicorn", "scripts.api_sentra:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
