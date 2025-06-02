FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./app /app/app 

CMD ["python", "-u", "app/main.py"]
