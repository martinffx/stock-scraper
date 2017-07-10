from sqlalchemy import (Table, Column, Integer, String, MetaData, Time, Date,
                        PrimaryKeyConstraint, BigInteger, Float)

meta = MetaData()

index = Table('index', meta,
              Column('exchange', String(10), nullable=False),
              Column('code', String(10), nullable=False),
              Column('name', String(255), nullable=False),
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

security = Table('security', meta,
                 Column('exchange_code', String(10), nullable=False),
                 Column('code', String(20), nullable=False),
                 Column('name', String(255), nullable=False),
                 Column('ccy', String(3), nullable=False),
                 Column('price_divisor', Integer, nullable=False),
                 PrimaryKeyConstraint(
                     'exchange_code', 'code', name='security_pk'))

security_index = Table('security_index', meta,
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

price_eod = Table('price_eod', meta,
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


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    index.create()
    security.create()
    security_index.create()
    price_eod.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    index.drop()
    security.drop()
    security_index.drop()
    price_eod.drop()
