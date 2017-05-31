from lxml import html
import requests
import json

from stock_scraper.schema import Share, Index

INDEX_RANGE = 'Index!A2:D'


class IndexService:
    """The index service encapsulates getting index data."""
    NULL_RECORD = Index.build(['[]', '[]', '[]', '[]'])

    def __init__(self, sheet, share, session):
        self.sheet = sheet
        self.share = share
        self.session = session

    def get(self, code):
        index = self.__get(code)
        if index == None:
            index = IndexService.NULL_RECORD
        return index

    def update(self):
        """Update the list of indexes stored in the database from the sheet"""
        indexes = self.__list()
        for index in indexes:
            self.session.add(index)
            self.session.commit()

    def update_constituents(self, index):
        """Update the shares that consitute this index in the databases"""
        if index == None:
            raise ValueError('index can not be None')

        if index == IndexService.NULL_RECORD:
            return

        pages = [
            self.__get_page(index, page) for page in range(1, index.pages + 1)
        ]
        shares = [share for page in pages for share in page]
        for share in shares:
            self.share.save(share)

    def update_shares(self, index, start_date, end_date):
        """Update the price data for all the shares in the index for the period"""
        shares = self.share.get(index=index)
        for share in shares:
            self.share.update(share, start_date, end_date)

    def __get_page(self, index, page):
        result = requests.get(index.url + '1')
        tree = html.fromstring(result.json()['html'])
        rows = tree.xpath('//table//tbody//tr')
        return [Share.build(row, index) for row in rows]

    def __list(self):
        result = self.sheet.get_values(INDEX_RANGE)
        values = result.get('values', [])

        if not values:
            return []

        return [Index.build(value) for value in values]

    def __get(self, code):
        return self.session.query(Index).filter(Index.code == code).first()
