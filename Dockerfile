FROM python:3

ADD my_script.py /

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

CMD [ "python", "bot.py" ]