import click
from datetime import datetime, timedelta
from click_datetime import Datetime
from stock_scraper.scraper import ScraperService

DEFAULT_DATE = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
DATE_FORMAT = '%Y-%m-%d'
INDEX = 'index'
SHARE = 'share'
FLAGS = '--noauth_local_webserver'


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
