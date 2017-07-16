import logging
import click
import os
from datetime import datetime, timedelta
from click_datetime import Datetime
from stock_scraper.service import (update_indexes, update_index,
                                   fetch_update_security, DATE_FORMAT)

DEFAULT_DATE = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
INDEX = 'index'
SHARE = 'share'

ROOT = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
@click.command()
def main(code, start_date, end_date, asset):
    """Stock Scraper pulls end of day data and index information from a
    Google Sheet and stores it in a database. Code is the index or
    share code to pull data for, if the index switch is passed all shares for
    that index is updated. If no code is provided all shares in all
    indexes will be updated."""

    if code is None:
        logger.info('update with shares')
        update_indexes(start_date, end_date)
        return

    if asset == INDEX:
        logger.info('update index')
        update_index(code, start_date, end_date)
        return

    if asset == SHARE:
        logger.info('update share')
        fetch_update_security(code, start_date, end_date)
        return


if __name__ == '__main__':
    handler = logging.FileHandler(os.environ['ENV'] + '.log')
    logging.getLogger(__name__).addHandler(handler)
    main()
