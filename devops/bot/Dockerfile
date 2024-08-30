FROM python:3.8

# Установка пакетов Python3 и Pip
#RUN apt-get update && apt-get install -y python3-pip

# Установка пакетов paramiko, psycopg2 и python-telegram-bot
RUN pip3 install paramiko psycopg2 python-telegram-bot==13.7

# Копирование вашего приложения в контейнер
COPY . .

EXPOSE 5000

# Запуск вашего приложения
CMD ["python3", "bot.py"]
