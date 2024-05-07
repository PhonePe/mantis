FROM --platform=linux/amd64 python:3.12-slim

RUN apt-get update -y && apt-get upgrade -y

# Setup work directory
WORKDIR /home/

# Copy requirements.txt for mantis
COPY ./requirements.txt /home/requirements.txt

RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000 

