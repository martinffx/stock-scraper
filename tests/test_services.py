import os
import json
import unittest
import unittest.mock as mock
import requests_mock

from stock_scraper.service import IndexService
from stock_scraper.google import SheetService
from stock_scraper.repository import Repository


class IndexServiceTest(unittest.TestCase):
    indexes = [[
        'FTSE 100 Index', 'FTSE:FSI', 'LSE', 'GBP', '1', ':', '08:00:00 UTC',
        '16:30:00 UTC', '', '', '6',
        'https://markets.ft.com/data/indices/ajax/getindexconstituents?xid=572009&pagenum='
    ], [
        'S&P 500 INDEX', 'INX:IOM', 'NYSE', 'USD', '1', ':', '14:30:00 UTC',
        '21:00:00 UTC', '', '', '26',
        'https://markets.ft.com/data/indices/ajax/getindexconstitnuents?xid=575769&pagenum='
    ]]

    def setUp(self):
        super(IndexServiceTest, self).setUp()
        self.sheet = mock.create_autospec(SheetService)
        self.repo = mock.create_autospec(Repository)
        self.service = IndexService(self.sheet, self.repo)

    def test_update_with_shares(self):
        self.sheet.get_values = mock.Mock(
            return_value={'values': self.indexes})

        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures/index_shares.json')

        with open(fixture, 'r') as f:
            rs = json.load(f)

        with requests_mock.Mocker() as m:
            [
                m.get(index[11] + str(x), json=rs)
                for index in self.indexes
                for x in range(1, int(index[10]) + 1)
            ]
            self.service.update_with_shares()

        self.repo.update_indexes.assert_called_once()
        self.repo.update_securities.assert_called()

    def test_update_with_shares_empty(self):
        self.sheet.get_values = mock.Mock(return_value={'xxxxx': [[], []]})
        self.service.update_with_shares()

        self.repo.update_indexes.assert_called_once()

    def test_update_index(self):
        self.sheet.get_values = mock.Mock(
            return_value={'values': self.indexes})

        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures/index_shares.json')

        with open(fixture, 'r') as f:
            rs = json.load(f)

        with requests_mock.Mocker() as m:
            [
                m.get(index[11] + str(x), json=rs)
                for index in self.indexes
                for x in range(1, int(index[10]) + 1)
            ]
            self.service.update_index('FTSE:FSI')

        self.repo.update_index.assert_called_once()
        self.repo.update_securities.assert_called()

    def test_update_index_invalid_code(self):
        self.sheet.get_values = mock.Mock(
            return_value={'values': self.indexes})
        self.service.update_index('sds')

        self.repo.update_indexes.assert_not_called()
        self.repo.update_securities.assert_not_called()
        self.repo.update_index.assert_not_called()
        self.repo.update_security.assert_not_called()
