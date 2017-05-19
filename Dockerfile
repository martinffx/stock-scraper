FROM python:3.6.1-slim

COPY ./ /usr/src/stock-scaper
WORKDIR /usr/src/stock-scaper

RUN pip install -r requirements.txt

CMD ["python", "quickstart.py"]
