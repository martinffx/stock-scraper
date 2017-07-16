import pdb
import logging
import json
from datetime import datetime
import pytz
from sqlalchemy import (Table, Column, Integer, String, MetaData, Time, Date,
                        PrimaryKeyConstraint, BigInteger, Float)
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)
meta = MetaData()

TIME_FORMAT = '%H:%M:%S %Z'
NULL_TIME = '00:00:00 UTC'
UTC = pytz.utc


def get_time(value):
    """Convert string into time, all time is considered UTC."""
    if not value:
        value = NULL_TIME
    return datetime.strptime(value, TIME_FORMAT).replace(tzinfo=UTC).timetz()


class Record:
    def __eq__(self, other):
        return self.data() == other.data()

    def upsert(self):
        insert_stmt = insert(self.schema).values(self.data())
        return insert_stmt.on_conflict_do_update(
            constraint=self.schema.primary_key, set_=self.data())

    def json(self):
        return json.dumps(self.data(), default=str)


class IndexRecord(Record):
    schema = Table('index', meta,
                   Column('exchange', String(10), nullable=False),
                   Column('code', String(10), nullable=False),
                   Column('name', String(255), nullable=False),
                   Column('provider', String(10), nullable=False),
                   Column('ccy', String(3), nullable=False),
                   Column('price_divisor', Float, nullable=False),
                   Column('separator', String(5), nullable=False),
                   Column('open', Time(True), nullable=False),
                   Column('close', Time(True), nullable=False),
                   Column('lunch_start', Time(True), nullable=False),
                   Column('lunch_end', Time(True), nullable=False),
                   Column('pages', Integer, nullable=False),
                   Column('url', String(1000), nullable=False),
                   PrimaryKeyConstraint('exchange', 'code', name='index_pk'))

    def __init__(self,
                 exchange=None,
                 name=None,
                 code=None,
                 provider=None,
                 ccy=None,
                 price_divisor=None,
                 separator=None,
                 open=None,
                 close=None,
                 lunch_start=None,
                 lunch_end=None,
                 pages=None,
                 url=None):
        self.exchange = exchange
        self.name = name
        self.code = code
        self.provider = provider
        self.ccy = ccy
        self.price_divisor = price_divisor
        self.separator = separator
        self.open = open
        self.close = close
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.pages = pages
        self.url = url

    def data(self):
        return {
            'exchange': self.exchange,
            'name': self.name,
            'code': self.code,
            'provider': self.provider,
            'ccy': self.ccy,
            'price_divisor': self.price_divisor,
            'separator': self.separator,
            'open': self.open,
            'close': self.close,
            'lunch_start': self.lunch_start,
            'lunch_end': self.lunch_end,
            'pages': self.pages,
            'url': self.url
        }

    @classmethod
    def build(cls, row):
        return cls(
            exchange=row[2],
            name=row[0],
            code=row[1],
            provider=row[3],
            ccy=row[4],
            price_divisor=float(row[5]),
            separator=row[6],
            open=get_time(row[7]),
            close=get_time(row[8]),
            lunch_start=get_time(row[9]),
            lunch_end=get_time(row[10]),
            pages=int(row[11]),
            url=row[12])

    @classmethod
    def build_from_repo(cls, repo):
        return cls(
            exchange=repo[0],
            code=repo[1],
            name=repo[2],
            provider=repo[3],
            ccy=repo[4],
            price_divisor=repo[5],
            separator=repo[6],
            open=repo[7],
            close=repo[8],
            lunch_start=repo[9],
            lunch_end=repo[10],
            pages=repo[11],
            url=repo[12])

    @classmethod
    def build_from_json(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        return cls(
            exchange=data['exchange'],
            code=data['code'],
            name=data['name'],
            provider=data['provider'],
            ccy=data['ccy'],
            price_divisor=data['price_divisor'],
            separator=data['separator'],
            open=data['open'],
            close=data['close'],
            lunch_start=data['lunch_start'],
            lunch_end=data['lunch_end'],
            pages=data['pages'],
            url=data['url'])


class SecurityRecord(Record):
    schema = Table('security', meta,
                   Column('exchange_code', String(10), nullable=False),
                   Column('code', String(20), nullable=False),
                   Column('name', String(255), nullable=False),
                   Column('ccy', String(3), nullable=False),
                   Column('price_divisor', Integer, nullable=False),
                   PrimaryKeyConstraint(
                       'exchange_code', 'code', name='security_pk'))

    def __init__(self,
                 exchange_code=None,
                 code=None,
                 name=None,
                 ccy=None,
                 price_divisor=None):
        self.exchange_code = exchange_code
        self.code = code
        self.name = name
        self.ccy = ccy
        self.price_divisor = price_divisor

    def data(self):
        return {
            'exchange_code': self.exchange_code,
            'code': self.code,
            'name': self.name,
            'ccy': self.ccy,
            'price_divisor': self.price_divisor
        }

    def ticker(self):
        return self.exchange_code + ':' + self.code

    @classmethod
    def build(cls, tree, index):
        codes = tree.xpath('td//span')[0].xpath('text()')[0].split(
            index.separator)
        name = tree.xpath('td//a/text()')[0]

        return cls(
            exchange_code=index.exchange,
            code=codes[0],
            name=name,
            ccy=index.ccy,
            price_divisor=index.price_divisor)

    @classmethod
    def build_from_repo(cls, repo):
        return cls(
            exchange_code=repo[0],
            code=repo[1],
            name=repo[2],
            ccy=repo[3],
            price_divisor=repo[4])

    @classmethod
    def build_from_json(cls, data):
        if isinstance(json, str):
            data = json.loads(data)
        return cls(
            exchange_code=data['exchange_code'],
            code=data['code'],
            name=data['name'],
            ccy=data['ccy'],
            price_divisor=data['price_divisor'])


class SecurityIndexRecord(Record):
    schema = Table('security_index', meta,
                   Column('security_exchange', String(10), nullable=False),
                   Column('security_code', String(10), nullable=False),
                   Column('index_exchange', String(10), nullable=False),
                   Column('index_code', String(10), nullable=False),
                   PrimaryKeyConstraint(
                       'security_exchange',
                       'security_code',
                       'index_exchange',
                       'index_code',
                       name='security_index_pk'))

    def __init__(self,
                 security_exchange=None,
                 security_code=None,
                 index_exchange=None,
                 index_code=None):
        self.security_exchange = security_exchange,
        self.security_code = security_code,
        self.index_exchange = index_exchange,
        self.index_code = index_code

    def data(self):
        return {
            'security_exchange': self.security_exchange,
            'security_code': self.security_code,
            'index_exchange': self.index_exchange,
            'index_code': self.index_code
        }

    @classmethod
    def build(cls, security, index):
        return cls(
            security_exchange=index.exchange,
            security_code=security.code,
            index_exchange=index.exchange,
            index_code=index.code)


class PriceEODRecord(Record):
    schema = Table('price_eod', meta,
                   Column('code', String(10), nullable=False),
                   Column('exchange_code', String(10), nullable=False),
                   Column('date', Date, nullable=False),
                   Column('open', BigInteger, nullable=False),
                   Column('low', BigInteger, nullable=False),
                   Column('high', BigInteger, nullable=False),
                   Column('close', BigInteger, nullable=False),
                   Column('volume', BigInteger, nullable=False),
                   PrimaryKeyConstraint(
                       'code', 'exchange_code', 'date', name='price_eod_pk'))

    def __init__(self,
                 code=None,
                 exchange_code=None,
                 date=None,
                 open=None,
                 low=None,
                 high=None,
                 close=None,
                 volume=None):
        self.code = code
        self.exchange_code = exchange_code
        self.date = date
        self.open = open
        self.low = low
        self.high = high
        self.close = close
        self.volume = volume

    def data(self):
        return {
            'code': self.code,
            'exchange_code': self.exchange_code,
            'date': self.date,
            'open': self.open,
            'low': self.low,
            'high': self.high,
            'close': self.close,
            'volume': self.volume
        }

    @classmethod
    def build_from_dt(cls, security, date, row):
        logger.debug(security.data())
        logger.debug(date)
        logger.debug(row)

        open = int(row[0] / security.price_divisor)
        high = int(row[1] / security.price_divisor)
        low = int(row[2] / security.price_divisor)
        close = int(row[3] / security.price_divisor)

        return cls(
            code=security.code,
            exchange_code=security.exchange_code,
            date=date,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=row[4])
