FROM ubuntu:latest
MAINTAINER Roman Myronenko 'eoma575@gmail.com'
RUN apt update -qy
RUN apt install -qy python3.11 python3-pip python3.11-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "bot/bot.py"]