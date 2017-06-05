FROM python:3.6.1-slim

COPY ./ /usr/src/stock-scaper
WORKDIR /usr/src/stock-scaper

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git

RUN pip install -r requirements.txt
RUN python manage.py upgrade

CMD ["python", "quickstart.py"]
