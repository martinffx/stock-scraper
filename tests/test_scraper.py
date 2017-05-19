import unittest
import unittest.mock as mock

from stock_scraper.scraper import ScraperService, DEFAULT_DATE
from stock_scraper.index import IndexService, IndexRecord
from stock_scraper.share import ShareService, ShareRecord

class ScraperServiceTest(unittest.TestCase):

    def setUp(self):
        self.share = mock.create_autospec(ShareService)
        self.index = mock.create_autospec(IndexService)
        self.service = ScraperService(self.index, self.share)


    def test_list_indexes(self):
        self.index.list = mock.Mock(return_value=[[]])
        indexes = self.service.list_indexes()

        self.index.list.assert_called()
        self.assertEqual(len(indexes), 1)

    def test_get_index(self):
        index_record = mock.create_autospec(IndexRecord)
        self.index.get = mock.Mock(return_value=index_record)

        index = self.service.get_index('CODE')
        self.assertIsInstance(index, IndexRecord)

    def test_update_index(self):
        index = mock.create_autospec(IndexRecord)
        self.index.get = mock.Mock(return_value=index)

        self.service.update_index('CODE', DEFAULT_DATE, DEFAULT_DATE)
        self.index.update.assert_called_with(index, DEFAULT_DATE, DEFAULT_DATE)
        self.index.get.assert_called_with('CODE')

    def test_get_share(self):
        share_record = mock.create_autospec(ShareRecord)
        self.share.get = mock.Mock(return_value=share_record)

        share = self.service.get_share('CODE')
        self.assertIsInstance(share, ShareRecord)
        self.share.get.assert_called_with('CODE')

    def test_update_share(self):
        self.service.update_share('CODE', DEFAULT_DATE, DEFAULT_DATE)
        self.share.update.assert_called_with('CODE', DEFAULT_DATE,
                                             DEFAULT_DATE)
