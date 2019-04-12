FROM python:3

WORKDIR /bot
RUN apt-get update
RUN apt-get install -y ffmpeg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=..

WORKDIR /bot/modular_bot

CMD [ "python", "./modular_bot.py" ]

