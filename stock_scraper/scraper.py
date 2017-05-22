import click
from datetime import datetime, timedelta
from click_datetime import Datetime

DEFAULT_DATE = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
DATE_FORMAT = '%Y-%m-%d'
INDEX = 'index'
SHARE = 'share'
FLAGS = '--noauth_local_webserver'

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
    def build(cls):
        sheet = SheetService(FLAGS)
        return cls(IndexService(sheet), ShareService(sheet))

    def list_indexes(self):
        """Fetch list of available indexes from the Google Sheet."""
        return self.index.list()

    def get_index(self, code):
        return self.index.get(code)

    def update_index(self, code, start_date, end_date):
        index = self.index.get(code)
        self.index.update_shares(index, start_date, end_date)

    def get_share(self, code):
        return self.share.get(code)

    def update_share(self, code, start_date, end_date):
        self.share.update(code, start_date, end_date)


@click.group()
@click.argument('code', required=False)
@click.option(
    '--start-date',
    type=Datetime(format=DATE_FORMAT),
    default=DEFAULT_DATE,
    help='''Start Date of Period''')
@click.option(
    '--end-date',
    type=Datetime(format=DATE_FORMAT),
    default=DEFAULT_DATE,
    help='''End Date of Period''')
@click.option(
    '--index',
    'asset',
    flag_value=INDEX,
    help='''Indicate that the provided code is for an index''')
@click.option(
    '--share',
    'asset',
    flag_value=SHARE,
    help='''Indicates that the provided code is for an share''',
    default=True)
def main(code, start_date, end_date, asset):
    """Stock Scraper pulls end of day data and index information from a
    Google Sheet and stores it in a database. Code is the index or
    share code to pull data for, if the index switch is passed all shares for
    that index is updated. If no code is provided all shares in all
    indexes will be updated."""
    service = ScraperService.build(FLAGS)
    if code is None:
        indexes = service.list_indexes()
        for index in indexes:
            service.update_index(index, start_date, end_date)
        return

    if asset == INDEX:
        index = service.get_index(code)
        if index is None:
            raise ValueError('Unknown index code, please ensure an index' +
                             'with that code is in the sheet.')
        service.update_index(index)
        return

    if asset == SHARE:
        share = service.get_share(code)
        service.update_share(share)
        return


if __name__ == '__main__':
    main()
