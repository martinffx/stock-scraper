import os
import unittest
import json
from lxml import html
import migrate.versioning.api as db

from tests.test import TestMixin
from stock_scraper.repository import Repository
from stock_scraper.records import (IndexRecord, SecurityRecord,
                                   SecurityIndexRecord)


class RepositoryTest(unittest.TestCase, TestMixin):
    def setUp(self):
        db.upgrade(os.environ['DATABASE_URL'], 'migrations')
        self.repo = Repository(os.environ['DATABASE_URL'])

    def tearDown(self):
        db.downgrade(os.environ['DATABASE_URL'], 'migrations', 0)

    def test_update_indexes(self):
        indexes = [
            IndexRecord.build(row)
            for row in self.load_fixture('fixtures/sheet_indexes.json')
        ]
        self.repo.update_indexes(indexes)
        results = self.repo.list_indexes()

        for result in results:
            self.assertTrue(result in indexes)

    def test_update_index(self):
        fixture = next(iter(self.load_fixture('fixtures/sheet_indexes.json')))
        index = IndexRecord.build(fixture)
        self.repo.update_index(index)
        result = self.repo.get_index(index.code)
        self.assertTrue(result == index)

    def test_update_securities(self):
        index = IndexRecord.build(
            self.load_fixture('fixtures/sheet_indexes.json')[0])
        securities = [
            SecurityRecord.build(row, index)
            for row in self.__get_securities()
        ]
        security_indexes = [
            SecurityIndexRecord.build(security, index)
            for security in securities
        ]
        self.repo.update_securities(securities)
        self.repo.update_security_indexes(security_indexes)
        results = self.repo.list_securities(index=index)

        for result in results:
            self.assertTrue(result in securities)

    def __get_securities(self):
        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures/index_shares.json')
        with open(fixture, 'r') as f:
            tree = html.fromstring(json.load(f)['html'])
        return tree.xpath('//table//tbody//tr')
