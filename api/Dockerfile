FROM python:3.11-alpine

WORKDIR /bot_api_app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .