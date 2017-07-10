import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.sql import select, and_
from stock_scraper.records import (IndexRecord, SecurityRecord,
                                   SecurityIndexRecord)

logger = logging.getLogger(__name__)


class Repository:
    NULL_INDEX = IndexRecord()

    def __init__(self, database_url):
        self.log = logging.getLogger('repository')
        self.engine = create_engine(database_url, pool_size=20, max_overflow=0)

    def list_indexes(self):
        results = self.__list(select([IndexRecord.schema]))
        return [IndexRecord.build_from_repo(result) for result in results]

    def get_index(self, code):
        stmt = select([IndexRecord.schema]).where(
            IndexRecord.schema.c.code == code)
        result = self.__get(stmt)
        return IndexRecord.build_from_repo(result)

    def update_indexes(self, indexes):
        self.log.info('save indexes')
        self.__update_all(indexes)

    def update_index(self, index):
        self.__update(index)

    def update_security_index(self, security_index):
        self.__update(security_index)

    def list_securities(self, index=None):
        query = select([SecurityRecord.schema])
        if index is not None:
            query.where(
                and_(SecurityRecord.schema.c.code ==
                     SecurityIndexRecord.schema.c.security_code,
                     SecurityRecord.schema.c.exchange_code ==
                     SecurityIndexRecord.schema.c.security_exchange, index.code
                     == SecurityIndexRecord.schema.c.index_code, index.code ==
                     SecurityIndexRecord.schema.c.index_exchange))
        logger.info(query)
        results = self.__list(query)
        return [SecurityRecord.build_from_repo(result) for result in results]

    def get_security(self, exchange, code):
        stmt = select([SecurityRecord.schema]).where(
            and_(SecurityRecord.schema.c.code == code,
                 SecurityRecord.schema.c.exchange_code == exchange))
        result = self.__get(stmt)
        return SecurityRecord.build_from_repo(result)

    def update_securities(self, securities):
        self.log.info('save securities')
        self.__update_all(securities)

    def update_security(self, security):
        self.__update(security)

    def update_security_indexes(self, security_indexes):
        self.log.info('save security indexes')
        self.__update_all(security_indexes)

    def update_price_eod(self, price_eod):
        self.__update(price_eod)

    def __list(self, select):
        logger.info(select)
        with self.engine.connect() as conn:
            return conn.execute(select)

    def __get(self, select):
        logger.info(select)
        with self.engine.connect() as conn:
            return conn.execute(select).first()

    def __update(self, record):
        self.__update_all([record])

    def __update_all(self, records):
        if not records:
            return

        with self.engine.connect() as conn:
            for record in records:
                conn.execute(record.upsert())


database_url = os.environ['DATABASE_URL']
repo = Repository(database_url)
