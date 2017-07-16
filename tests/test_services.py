import os
import unittest
import unittest.mock as mock
import requests_mock
from tests.test import TestMixin
from stock_scraper.repository import Repository
import migrate.versioning.api as db
from stock_scraper.service import (
    update_indexes, update_index, fetch_update_security, update_price_task,
    update_constituents_task, update_security_task)
from main import DEFAULT_DATE

index_data = '{"data": {"exchange": "NYSE", "name": "S&P 500 INDEX", "code": "INX:IOM", "provider": "GOOGLE", "ccy": "USD", "price_divisor": 0.01, "separator": ":", "open": "14:30:00+00:00", "close": "21:00:00+00:00", "lunch_start": "00:00:00+00:00", "lunch_end": "00:00:00+00:00", "pages": 26, "url": "https://markets.ft.com/data/indices/ajax/getindexconstitnuents?xid=575769&pagenum="}, "start": "2017-07-15", "end": "2017-07-15"}'


class ServiceTest(unittest.TestCase, TestMixin):
    def setUp(self):
        db.upgrade(os.environ['DATABASE_URL'], 'migrations')
        self.repo = Repository(os.environ['DATABASE_URL'])

    def tearDown(self):
        db.downgrade(os.environ['DATABASE_URL'], 'migrations', 0)

    @mock.patch('stock_scraper.service.repo')
    @mock.patch('stock_scraper.service.sheet')
    @mock.patch('stock_scraper.service.update_constituents_task')
    def test_update_indexes(self, mock_update_constituents_task, mock_sheet,
                            mock_repo):
        indexes = self.load_fixture('fixtures/sheet_indexes.json')
        mock_sheet.get_values = mock.Mock(return_value={'values': indexes})

        with requests_mock.Mocker() as m:
            [
                m.get(index[11] + str(x), json=indexes)
                for index in indexes for x in range(1, int(index[11]) + 1)
            ]
            update_indexes(DEFAULT_DATE, DEFAULT_DATE)

        mock_repo.update_indexes.assert_called_once()
        mock_update_constituents_task.delay.assert_called_with(index_data)

    @mock.patch('stock_scraper.service.repo')
    @mock.patch('stock_scraper.service.sheet')
    @mock.patch('stock_scraper.service.update_constituents_task')
    def test_update_index(self, mock_update_constituents_task, mock_sheet,
                          mock_repo):
        indexes = self.load_fixture('fixtures/sheet_indexes.json')
        mock_sheet.get_values = mock.Mock(return_value={'values': indexes})

        update_index('NYSE', DEFAULT_DATE, DEFAULT_DATE)

        mock_repo.update_index.assert_called_once()
        mock_update_constituents_task.delay.assert_called_with(index_data)

    @mock.patch('stock_scraper.service.sheet')
    @mock.patch('stock_scraper.service.repo')
    @mock.patch('stock_scraper.service.update_price_task')
    def test_fetch_update_security(self, mock_update_price_task, mock_repo,
                                   mock_sheet):
        mock_repo.get_security = mock.Mock(
            return_value=Repository.NULL_SECURITY)
        fetch_update_security('FTSE:FSI', DEFAULT_DATE, DEFAULT_DATE)

        mock_update_price_task.delay.assert_called_with(
            '{"data": {"exchange_code": null, "code": null, "name": null, "ccy": null, "price_divisor": null}, "start": "2017-07-15", "end": "2017-07-15"}'
        )

    @mock.patch('stock_scraper.service.web')
    @mock.patch('stock_scraper.service.repo')
    def test_update_price_task(self, mock_repo, mock_web):
        data_str = '{"data": {"exchange_code": "NYSE", "code": "F", "name": "Facebook", "ccy": "USD", "price_divisor": 0.01}, "start": "2017-07-15 00:00:00", "end": "2017-07-15 00:00:00"}'
        prices = self.load_csv('fixtures/prices.csv')
        mock_web.DataReader = mock.Mock(return_value=prices)
        update_price_task(data_str)
        mock_repo.update_price_eod.assert_called()

    @mock.patch('stock_scraper.service.repo')
    @mock.patch('stock_scraper.service.update_price_task')
    def test_update_security_task(self, mock_update_price_task, mock_repo):
        url = 'https://markets.ft.com/data/indices/ajax/getindexconstituents?xid=572009&pagenum=1'
        update_security_task(index_data, url)

        mock_update_price_task.delay.assert_called_with(
            '{"data": {"exchange_code": "NYSE", "code": "CCL", "name": "Carnival PLC", "ccy": "USD", "price_divisor": 0.01}, "start": "2017-07-15", "end": "2017-07-15"}'
        )
        mock_repo.update_security.assert_called()
        mock_repo.update_security_index.assert_called()

    @mock.patch('stock_scraper.service.update_security_task')
    def test_update_constituents_task(self, mock_update_security_task):
        update_constituents_task(index_data)
        mock_update_security_task.delay.assert_called_with(
            index_data,
            'https://markets.ft.com/data/indices/ajax/getindexconstitnuents?xid=575769&pagenum=26'
        )
