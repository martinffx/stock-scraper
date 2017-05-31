import unittest
import unittest.mock as mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from stock_scraper.share import ShareService
from stock_scraper.price import PriceService
from stock_scraper.scraper import DEFAULT_DATE
from stock_scraper.schema import Index, Share, Base
from test import DBTestCase


class ShareServiceTest(DBTestCase):
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        self.price = mock.create_autospec(PriceService)
        self.service = ShareService(self.price, self.session)
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_save(self):
        index = Index.build(['', 'xx', '', ''])
        share = Share(index=index, code='jsq:agl', name='')
        self.service.save(share)

    def test_update(self):
        share = mock.create_autospec(Share)
        self.price.get_data = mock.Mock(return_value=[])
        self.service.update(share, DEFAULT_DATE, DEFAULT_DATE)
        self.price.get_data.assert_called_with(share, DEFAULT_DATE,
                                               DEFAULT_DATE)
        self.price.save.assert_called_with([])
