FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.29.0 \
    requests==2.32.3 \
    pydantic==2.11.0

COPY mcp /app/mcp

CMD ["uvicorn", "mcp.server:app", "--host", "0.0.0.0", "--port", "8400"]
