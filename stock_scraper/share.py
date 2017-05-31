from stock_scraper.schema import Index, Share


class ShareService:
    """Manage share information"""

    def __init__(self, price_service, session):
        self.price = price_service
        self.session = session

    def save(self, share):
        self.session.add(share)
        self.session.commit()

    def update(self, share, start_date, end_date):
        data = self.price.get_data(share, start_date, end_date)
        self.price.save(data)
