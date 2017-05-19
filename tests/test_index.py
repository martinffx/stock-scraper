import unittest
import unittest.mock as mock
import requests_mock
import json
import os

from stock_scraper.scraper import DEFAULT_DATE
from stock_scraper.index import IndexService, IndexRecord
from stock_scraper.sheet import SheetService
from stock_scraper.share import ShareService, ShareRecord

class IndexServiceTest(unittest.TestCase):

    def setUp(self):
        self.sheet = mock.create_autospec(SheetService)
        self.share = mock.create_autospec(ShareService)
        self.service = IndexService(self.sheet, self.share)


    def test_list(self):
        self.sheet.get_values = mock.Mock(return_value={'values':
                                                        [['', '', '', ''],
                                                         ['', '', '', '']]})

        indexes = self.service.list()
        for index in indexes:
            self.assertIsInstance(index, IndexRecord)

    def test_get_from_code(self):
        self.sheet.get_values = mock.Mock(return_value={'values':
                                                        [['', 'xx', '', ''],
                                                         ['', 'yy', '', '']]})

        index = self.service.get('xx')
        self.assertEqual('xx', index.code)

    def test_get_from_missing_code(self):
        self.sheet.get_values = mock.Mock(return_value={'values':
                                                        [['', 'xx', '', ''],
                                                         ['', 'yy', '', '']]})

        index = self.service.get('zz')
        self.assertEqual(IndexService.NULL_RECORD, index)

    def test_update_none_should_raise_value_error(self):
        with self.assertRaises(ValueError):
            self.service.update(None, DEFAULT_DATE, DEFAULT_DATE)

    def test_update_null_should_return(self):
        self.service.update(IndexService.NULL_RECORD, DEFAULT_DATE, DEFAULT_DATE)


    def test_update_with_index(self):
        index = IndexRecord(['FTSE 100 Index', 'FTSE:FSI', 6, 'https://markets.ft.com/data/indices/ajax/getindexconstituents?xid=572009&pagenum='])
        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures/index_shares.json')
        with open(fixture, 'r') as f:
            rs = json.load(f)
        with requests_mock.Mocker() as m:
            [m.get(index.url + str(x), json=rs) for x in range(1,index.pages+1)]
            self.service.update(index, DEFAULT_DATE, DEFAULT_DATE)
