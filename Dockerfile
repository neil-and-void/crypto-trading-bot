FROM ubuntu:18.04

COPY . /usr/src/trading-bot

WORKDIR /usr/src/trading-bot

RUN set -xe \
    && apt-get update \
    && apt-get -y install python-pip

SHELL ["pip", "--version"]

RUN pip install pip --upgrade

RUN pip install -r requirements.txt

CMD [ "python", "bot.py", "run", "1" ]