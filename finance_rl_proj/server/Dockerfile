FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" 

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates liblzma-dev \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt . 
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]