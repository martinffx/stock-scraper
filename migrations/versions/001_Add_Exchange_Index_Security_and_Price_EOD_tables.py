from sqlalchemy import (Table, Column, Integer, String, MetaData, Time, Date,
                        DateTime, ForeignKeyConstraint, PrimaryKeyConstraint)

meta = MetaData()

exchange = Table('exchange', meta,
                 Column('code', String(5), nullable=False),
                 Column('name', String(255), nullable=False),
                 Column('open', Time(True), nullable=False),
                 Column('close', Time(True), nullable=False),
                 Column('first_valid', DateTime(True), nullable=False),
                 Column('last_valid', DateTime(True), nullable=False),
                 PrimaryKeyConstraint(
                     'code', 'last_valid', name='exchange_pk'))

index = Table('index', meta,
              Column('exchange_code', String(5), nullable=False),
              Column('code', String(5), nullable=False),
              Column('name', String(255), nullable=False),
              Column('pages', Integer, nullable=False),
              Column('url', String(255), nullable=False),
              Column('first_valid', DateTime(True), nullable=False),
              Column('last_valid', DateTime(True), nullable=False),
              PrimaryKeyConstraint(
                  'exchange_code', 'code', 'last_valid', name='index_pk'))

security = Table('security', meta,
                 Column('exchange_code', String(5), nullable=False),
                 Column('code', String(5), nullable=False),
                 Column('name', String(255), nullable=False),
                 Column('ccy', String(3), nullable=False),
                 Column('price_divisor', Integer(), nullable=False),
                 Column('first_valid', DateTime(True), nullable=False),
                 Column('last_valid', DateTime(True), nullable=False),
                 PrimaryKeyConstraint(
                     'exchange_code', 'code', 'last_valid',
                     name='security_pk'))

security_index = Table('security_index', meta,
                       Column('security_exchange', String(5), nullable=False),
                       Column('security_code', String(5), nullable=False),
                       Column('index_exchange', String(5), nullable=False),
                       Column('index_code', String(5), nullable=False),
                       Column('first_valid', DateTime(True), nullable=False),
                       Column('last_valid', DateTime(True), nullable=False),
                       PrimaryKeyConstraint(
                           'security_exchange',
                           'security_code',
                           'index_exchange',
                           'index_code',
                           'last_valid',
                           name='security_index_pk'))

price_eod = Table('price_eod', meta,
                  Column('security_code', String(5), nullable=False),
                  Column('exchange_code', String(5), nullable=False),
                  Column('date', Date(), nullable=False),
                  Column('open', Integer(), nullable=False),
                  Column('low', Integer, nullable=False),
                  Column('high', String(255), nullable=False),
                  Column('close', Time(True), nullable=False),
                  Column('volume', Time(True), nullable=False),
                  Column('first_valid', DateTime(True), nullable=False),
                  Column('last_valid', DateTime(True), nullable=False),
                  PrimaryKeyConstraint(
                      'security_code',
                      'exchange_code',
                      'date',
                      'last_valid',
                      name='price_eod_pk'))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    exchange.create()
    index.create()
    security.create()
    security_index.create()
    price_eod.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    exchange.drop()
    index.drop()
    security.drop()
    security_index.drop()
    price_eod.drop()
