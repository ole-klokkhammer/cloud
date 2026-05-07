FROM python:3.12-slim

WORKDIR /app

# Install dependencies for matrix-nio crypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    libolm-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
