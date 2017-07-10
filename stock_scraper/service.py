import os
import logging
import requests
import json
from datetime import datetime
from lxml import html
import pandas_datareader.data as web
from stock_scraper.records import (SecurityRecord, IndexRecord,
                                   SecurityIndexRecord, PriceEODRecord)
from stock_scraper.repository import repo, Repository
from stock_scraper.google import SheetService
from stock_scraper.tasks import app

logger = logging.getLogger(__name__)
connect_timeout, read_timeout = 5.0, 30.0

INDEX_RANGE = 'Index!A2:L'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = ' %H:%M:%S'

FLAGS = '--noauth_local_webserver'
home_dir = os.path.abspath(os.environ['GOOGLE_CREDENTIALS'])
sheet = SheetService(home_dir, FLAGS)


def msg(data, start, end):
    return json.dumps({'data': data, 'start': start, 'end': end}, default=str)


@app.task
def update_price(data_str):
    logger.debug(data_str)
    data = json.loads(data_str)
    security = SecurityRecord.build_from_json(data['data'])
    start_date = datetime.strptime(data['start'], DATE_FORMAT + TIME_FORMAT)
    end_date = datetime.strptime(data['end'], DATE_FORMAT + TIME_FORMAT)
    prices = web.DataReader(security.ticker(), 'google', start_date, end_date)
    for date, row in prices.iterrows():
        price = PriceEODRecord.build_from_dt(security, date, row)
        repo.update_price_eod(price)


def fetch_update_security(exchange_code, start_date, end_date):
    exchange, code = exchange_code.split(':')
    security = repo.get_security(exchange, code)
    update_price.delay(msg(security.data(), start_date, end_date))


@app.task
def get_page(data_json, url):
    logger.info(url)
    page = requests.get(url, timeout=(connect_timeout, read_timeout)).json()

    data = json.loads(data_json)
    logger.debug(data)
    index = IndexRecord.build_from_json(data['data'])
    start_date = data['start']
    end_date = data['end']
    tree = html.fromstring(page['html'])
    rows = tree.xpath('//table//tbody//tr')
    for row in rows:
        security = SecurityRecord.build(row, index)
        security_index = SecurityIndexRecord.build(security, index)
        update_price.delay(msg(security.data(), start_date, end_date))
        repo.update_security(security)
        repo.update_security_index(security_index)


@app.task
def update_constituents(data_json):
    """Update the shares that consitute this index in the databases"""
    data = json.loads(data_json)
    start_date = data['start']
    end_date = data['end']

    logger.debug(data)
    index = IndexRecord.build_from_json(data['data'])
    if index == Repository.NULL_INDEX:
        return

    logger.debug(index.data())
    for page in range(1, index.pages + 1):
        data = msg(index.data(), start_date, end_date)
        url = index.url + str(page)
        get_page.delay(data, url)


def update_indexes(start_date, end_date):
    """Updates all indexes and their constituents in the database"""
    indexes = __list()
    repo.update_indexes(indexes)
    for index in indexes:
        update_constituents.delay(msg(index.data(), start_date, end_date))


def update_index(code, start_date, end_date):
    """Update the index based off the code"""
    index = __get(code)

    logger.info(index.data())
    if index is not Repository.NULL_INDEX:
        repo.update_index(index)
        update_constituents.delay(msg(index.data(), start_date, end_date))


def __list():
    result = sheet.get_values(INDEX_RANGE)
    values = result.get('values', [])

    if not values:
        return []

    return [IndexRecord.build(value) for value in values]


def __get(code):
    indexes = __list()

    index = next(
        filter(lambda index: index.code == code, indexes),
        Repository.NULL_INDEX)
    return index
