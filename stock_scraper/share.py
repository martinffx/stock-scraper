from stock_scraper.schema import Index, Share


class ShareRepository:
    def __init__(self):
        pass

    def save(self, share):
        pass


class ShareService:
    """Manage share information"""

    def __init__(self, share_repo, price_service):
        self.repo = share_repo
        self.price = price_service

    def save(self, share):
        self.repo.save(share)

    def update(self, share, start_date, end_date):
        data = self.price.get(share, start_date, end_date)
        self.price.save(data)
