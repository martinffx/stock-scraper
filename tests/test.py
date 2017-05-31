import unittest
import unittest.mock as mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock_scraper.schema import Base


class DBTestCase(unittest.TestCase):
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
