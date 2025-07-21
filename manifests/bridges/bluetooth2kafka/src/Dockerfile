FROM python:3.13-alpine

RUN apg update && apk add --no-cache bluez > /dev/null 2>&1 || true

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./app /app/app 

CMD ["python", "app/main.py"]
