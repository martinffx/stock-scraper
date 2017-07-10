FROM python:3.6.1-slim

COPY ./ /usr/src/stock-scaper
WORKDIR /usr/src/stock-scaper

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git wget

ENV DOCKERIZE_VERSION v0.5.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN pip install -r requirements.txt
RUN chmod +x ./docker-entrypoint.sh

CMD ["dockerize -wait tcp://db:5432 docker-entrypoint.sh"]
