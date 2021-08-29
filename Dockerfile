FROM python:3.9-slim-buster

COPY . /trading-bot

WORKDIR /trading-bot

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN pip3 install pip --upgrade

RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py", "run"]