FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates liblzma-dev \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
RUN pip install --upgrade pip setuptools wheel

COPY pyproject.toml .
COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir .

CMD ["uvicorn", "finance_rl_proj.server.app:app", "--host", "0.0.0.0", "--port", "7860"]