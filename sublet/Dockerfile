FROM python:3.10.5

WORKDIR /telegram_bot

COPY . /telegram_bot

COPY media /media

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
