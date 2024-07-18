FROM python:3.10

RUN apt update && apt upgrade -y
RUN pip3 install paho-mqtt requests schedule

ADD ./app /app
WORKDIR /app

## make sure to log print statements
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "app.py"]