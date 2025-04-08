FROM python:3.11

WORKDIR /app
ADD ./app /app
RUN pip install --no-cache-dir -r requirements.txt

ENV API_PORT=8080
ENV HOST=0.0.0.0

CMD uvicorn app:app --host $HOST --port $API_PORT