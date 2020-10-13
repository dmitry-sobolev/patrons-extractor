FROM python:alpine

WORKDIR /opt/app

COPY . .

RUN apk add --no-cache git \
    && pip install -r requirements.txt \
    && apk del git

CMD ["python", "-u", "main.py"]