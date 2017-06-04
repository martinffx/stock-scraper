from lxml import html
import requests
from stock_scraper.schema import Share, Index

INDEX_RANGE = 'Index!A2:D'


class PriceService:
    def __init__(self, sheet, session):
        self.sheet = sheet
        self.session = session

    def get_data(self, share, start_date, end_date):
        query = [{
            'range':
            'Price!A1',
            'values': [[
                '=GOOGLEFINANCE("' + share.code + '", "all", "' + end_date +
                '", "' + start_date + '")'
            ]]
        }]
        self.sheet.gete_and_update()
        pass

    def save(self, prices):
        self.session.add_all(prices)
        self.commit()


class ShareService:
    """Manage share information"""

    def __init__(self, price_service, session):
        self.price = price_service
        self.session = session

    def save(self, share):
        self.session.add(share)
        self.session.commit()

    def save_all(self, shares):
        self.session.add_all(shares)
        self.session.commit()

    def wlupdate(self, share, start_date, end_date):
        data = self.price.get_data(share, start_date, end_date)
        self.price.save(data)


class IndexService:
    """The index service encapsulates getting index data."""
    NULL_RECORD = Index.build(['[]', '[]', '[]', '[]'])

    def __init__(self, sheet, share, session):
        self.sheet = sheet
        self.share = share
        self.session = session

    def update_with_shares(self):
        """Updates all indexes and their constituents in the database"""
        indexes = self.__list()
        self.__save_all(indexes)
        for index in indexes:
            self.__update_constituents(index)

    def update_index(self, code):
        """Update the index based off the code and all constituent shares"""
        index = self.__get(code)
        self.__save(index)
        self.__update_constituents(index)

    def __save(self, index):
        if index == IndexService.NULL_RECORD:
            return
        self.session.add(index)
        self.session.commit()

    def __save_all(self, indexes):
        self.session.add_all(indexes)
        self.session.commit()

    def __update_constituents(self, index):
        """Update the shares that consitute this index in the databases"""
        if index is None:
            raise ValueError('index can not be None')

        if index == IndexService.NULL_RECORD:
            return

        pages = [
            self.__get_page(index, page) for page in range(1, index.pages + 1)
        ]
        shares = [share for page in pages for share in page]
        for share in shares:
            self.share.save(share)

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
