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
