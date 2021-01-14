from datetime import timedelta

from models import StockPrice
from db_tools import connect_db, InteractDB
from config import START, END


class BackTest:
    def __init__(self, symbols, ratio):
        self.session = connect_db()
        self.symbols = symbols
        self.ratio = ratio

    def get_price_list(self):
        one_day = timedelta(days=1)
        price_list = []
        date_list = []
        for i, symbol in enumerate(self.symbols):
            day = START
            price_list_temp = []
            while True:
                day += one_day
                price = self._get_price(symbol, day)
                price_list_temp.append(price)
                if i == 0:
                    date_list.append(day)
                if day >= END:
                    break
            price_list.append(price_list_temp)
        return date_list, price_list

    def _get_price(self, symbol, date):
        instance = self.session.query(StockPrice).\
            filter(StockPrice.date==date).\
                filter(StockPrice.ticker_symbol==symbol).first()
        if instance:
            price = instance.price
            return price
        else:
            return

    def get_price_list_cumulative(self):
        idb = InteractDB()
        date_list, price_list = idb.get_price_list()
        price_list_cumulative = []
        for price_list_each in price_list:
            price_list_temp = []
            for price in price_list_each:
                if price:
                    price_list_temp.append(price_list_temp[-1]+price)
                else:
                    price_list_temp.append(price_list_temp[-1])
            price_list_cumulative.append(price_list_cumulative)
        return price_list_cumulative

    def get_portfolio_price_list(self, price_list):
        portfolio_price_list = []
        for i, price_list_temp in enumerate(price_list):
            if i == 0:
                portfolio_price_list =\
                    [price * self.ratio[i] if price else 0 for price in price_list_temp]
            else:
                for j, price in enumerate(price_list_temp):
                    if price:
                        portfolio_price_list[j] += price * self.ratio[i]
        return portfolio_price_list
