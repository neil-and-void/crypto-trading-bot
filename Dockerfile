FROM ubuntu:18.04

COPY . /trading-bot

WORKDIR /trading-bot

RUN set -xe \
    && apt-get update \
    && apt-get -y install python3-pip

RUN pip3 install pip --upgrade

RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py", "run"]