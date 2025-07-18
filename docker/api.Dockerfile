FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000  

RUN pip install packaging
CMD ["uvicorn", "scripts.api_sentra:app", "--host", "0.0.0.0", "--port", "8000"]
