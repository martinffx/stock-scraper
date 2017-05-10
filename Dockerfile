FROM 3.6.1-alpine

COPY ./ /usr/src/stock-scaper
WORKDIR /usr/src/stock-scaper

CMD ["python", "quickstart.py"]
