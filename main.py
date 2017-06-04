import click
import os
from datetime import datetime, timedelta
from click_datetime import Datetime
from stock_scraper.service import IndexService, ShareService, PriceService
from stock_scraper.google import SheetService
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DEFAULT_DATE = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
DATE_FORMAT = '%Y-%m-%d'
INDEX = 'index'
SHARE = 'share'
FLAGS = '--noauth_local_webserver'
ROOT = os.path.dirname(__file__)


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
@click.option(
    '--database-url',
    'database_url',
    default=None,
    help='''database to store results in, defaults to DATABASE_URL
    environment variable''')
@click.command()
def main(code, start_date, end_date, asset, database_url):
    """Stock Scraper pulls end of day data and index information from a
    Google Sheet and stores it in a database. Code is the index or
    share code to pull data for, if the index switch is passed all shares for
    that index is updated. If no code is provided all shares in all
    indexes will be updated."""
    home_dir = os.path.abspath(ROOT)
    if database_url is None:
        database_url = os.environ['DATABASE_URL']

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    sheet = SheetService(home_dir, FLAGS)
    price = PriceService(sheet, session)
    share = ShareService(price, session)
    index = IndexService(sheet, share)

    if code is None:
        index.update_with_shares()
        return

    if asset == INDEX:
        index.update_index(code)
        return

    if asset == SHARE:
        share.update_share(code)
        return


if __name__ == '__main__':
    main()
