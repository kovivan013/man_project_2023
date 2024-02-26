FROM python:3.11-alpine

WORKDIR /telegram_bot_app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "main.py"]