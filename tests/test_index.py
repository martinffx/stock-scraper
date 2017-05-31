import unittest
import unittest.mock as mock
import requests_mock
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from test import DBTestCase

from nose.tools import set_trace

from stock_scraper.scraper import DEFAULT_DATE
from stock_scraper.index import IndexService
from stock_scraper.schema import Index, Share, Base
from stock_scraper.sheet import SheetService
from stock_scraper.share import ShareService


class IndexServiceTest(DBTestCase):
    def setUp(self):
        super(IndexServiceTest, self).setUp()
        self.sheet = mock.create_autospec(SheetService)
        self.share = mock.create_autospec(ShareService)
        self.service = IndexService(self.sheet, self.share, self.session)

    def test_update_index_from_sheet(self):
        self.sheet.get_values = mock.Mock(
            return_value={'values': [['', 'xx', '', ''], ['', 'yy', '', '']]})
        self.service.update()

    def test_update_index_constituents(self):
        index = Index.build([
            'FTSE 100 Index', 'FTSE:FSI', 6,
            'https://markets.ft.com/data/indices/ajax/getindexconstituents?xid=572009&pagenum='
        ])
        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures/index_shares.json')

        with open(fixture, 'r') as f:
            rs = json.load(f)

        self.share.get = mock.Mock(return_value=[])
        with requests_mock.Mocker() as m:
            [
                m.get(index.url + str(x), json=rs)
                for x in range(1, index.pages + 1)
            ]
            self.service.update_constituents(index)

    def test_update_index_shares(self):
        pass

    def test_get_from_code(self):
        self.session.add(Index.build(['', 'xx', '', '']))
        self.session.commit()

        index = self.service.get('xx')
        self.assertEqual('xx', index.code)

    def test_get_from_missing_code(self):
        index = self.service.get('zz')
        self.assertEqual(IndexService.NULL_RECORD, index)
