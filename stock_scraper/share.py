from nose.tools import set_trace

class ShareRecord:

    def __init__(self, code, name, index):
        self.code = code
        self.name = name
        self.index = index

    @classmethod
    def build(cls, tree, index):
        code = tree.xpath('td//span')[0].xpath('text()')
        name = tree.xpath('td//a/text()')

        return cls(code, name, index.code)


class ShareRepository:

    def __init(self):
        pass

    def save(self, share):
        pass

class ShareService:
    """Manage share information"""

    def __init__(self, sheet_service, share_repo, price_service):
        self.sheet = sheet_service
        self.repo = share_repo
        self.price = price_service

    def save(self, share):
        self.repo.save(share)

    def update(self, share, start_date, end_date):
        data = self.price.get(code, start_date, end_date)
        self.price.save(data)

    def get(self, code):
        pass
