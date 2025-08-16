FROM python:3.13.7-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD [ "python", "-u", "./main.py"]