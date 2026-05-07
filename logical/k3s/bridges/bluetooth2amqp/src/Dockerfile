FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.11 python3.11-venv python3.11-distutils python3-pip bluez && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    apt clean

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app

CMD ["python3", "app/main.py"]