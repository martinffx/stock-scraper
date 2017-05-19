from lxml import html
import requests
import json

from stock_scraper.share import ShareRecord

INDEX_SHEET = '10sHdXR_NyQ-hxrEu7QALDX5qwuLWjCAfENSh2c3Cka4'
INDEX_RANGE = 'Index!A2:D'

class IndexRecord:

    def __init__(self, value):
        if value is None or len(value) != 4:
            raise ValueError('value must be 4 element list: ' +
                             '[name, code, pages, url]')
        self.name = value[0]
        self.code = value[1]
        self.pages = value[2]
        self.url = value[3]

class IndexService:
    """The index service encapsulates getting index data."""
    NULL_RECORD = IndexRecord([[], [], [], []])

    def __init__(self, sheet_service, share_service):
        self.sheet = sheet_service
        self.share = share_service

    def list(self):
        result = self.sheet.get_values(INDEX_SHEET, INDEX_RANGE)
        values = result.get('values', [])

        if not values:
            return []

        return [IndexRecord(value) for value in values]

    def get(self, code):
        indexes = self.list()
        result = next((index for index in indexes if index.code == code),
                      IndexService.NULL_RECORD)
        return result

    def update(self, index, start_date, end_date):
        if index == None:
            raise ValueError('index can not be None')

        if index == IndexService.NULL_RECORD:
            return

        pages = [self.__get_page(index, page) for page in
                 range(1, index.pages + 1)]
        shares = [share for page in pages for share in page]
        for share in shares:
            self.share.save(share)
            self.share.update(share, start_date, end_date)

    def __get_page(self, index, page):
        result = requests.get(index.url + '1')
        tree = html.fromstring(result.json()['html'])
        rows = tree.xpath('//table//tbody//tr')
        return [ShareRecord.build(row, index) for row in rows]
