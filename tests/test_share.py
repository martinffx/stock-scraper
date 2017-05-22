import unittest
import unittest.mock as mock

from stock_scraper.share import ShareRepository, ShareService
from stock_scraper.price import PriceService
from stock_scraper.scraper import DEFAULT_DATE
from stock_scraper.schema import Index, Share


class ShareServiceTest(unittest.TestCase):
    def setUp(self):
        self.price = mock.create_autospec(PriceService)
        self.repo = mock.create_autospec(ShareRepository)
        self.service = ShareService(self.repo, self.price)

    def test_save(self):
        index = Index()
        share = mock.create_autospec(Share)
        self.service.save(share)

    def test_update(self):
        share = mock.create_autospec(Share)
        self.price.get = mock.Mock(return_value=[])
        self.service.update(share, DEFAULT_DATE, DEFAULT_DATE)
        self.price.get.assert_called_with(share, DEFAULT_DATE, DEFAULT_DATE)
        self.price.save.assert_called_with([])
