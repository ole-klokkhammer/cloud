# python < 3.11
FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y curl gnupg ffmpeg
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install libedgetpu1-std -y 
# RUN apt-get update && apt-get install libedgetpu1-max -y 

WORKDIR /app  
COPY ./requirements.txt /app/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt 
COPY ./app /app/app 

CMD ["python", "app/main.py"]
