FROM python:3.12

WORKDIR /bot
VOLUME /bot

RUN apt-get update && apt-get install -y ffmpeg

COPY src/bot/requirements.txt .
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]