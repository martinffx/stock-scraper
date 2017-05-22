class PriceService:
    def __init__(self, sheet, repo):
        self.sheet = sheet
        self.repo = repo

    def get(self, share, start_date, end_date):
        pass

    def save(self, prices):
        for price in prices:
            self.repo.save(price)
