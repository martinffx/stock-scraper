from stock_scraper.index import IndexService
from stock_scraper.share import ShareService
from stock_scraper.sheet import SheetService


class ScraperService:
    """Core Service for managing the scraping and processing of
    various aspects of the application."""

    def __init__(self, index_service, share_service):
        self.index = index_service
        self.share = share_service

    @classmethod
    def build(cls, flags):
        sheet = SheetService(flags)
        return cls(IndexService(sheet), ShareService(sheet))

    def list_indexes(self):
        """Fetch list of available indexes from the Google Sheet."""
        return self.index.list()

    def update_index(self, index):
        """Takes in the index object, saves it to the database and
        updates all it's constituent shares"""
        self.index.save(index)
        self.index.update_shares(index)

    def update_index_and_price(self, code, start_date, end_date):
        self.index.update_shares_and_price(code, start_date, end_date)

    def get_share(self, code):
        return self.share.get(code)

    def update_share(self, code, start_date, end_date):
        self.share.update(code, start_date, end_date)
