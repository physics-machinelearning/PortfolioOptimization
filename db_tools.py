import os
from datetime import timedelta

from dotenv import load_dotenv
from sqlalchemy import create_engine, asc, or_
from sqlalchemy.orm import Session
import psycopg2
import pandas as pd

from models import Base, StockPrice, TickerSymbol
from config import START, END

load_dotenv()

POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_DB = os.environ['POSTGRES_DB']


def connect_db():
    engine = create_engine('postgresql://{user}:{password}@{host}/{db}'
                           .format(user=POSTGRES_USER,
                                   password=POSTGRES_PASSWORD,
                                   host=POSTGRES_HOST, db=POSTGRES_DB))
    session = Session(bind=engine)
    return session


def create_table():
    engine = create_engine('postgresql://{user}:{password}@{host}/{db}'
                           .format(user=POSTGRES_USER,
                                   password=POSTGRES_PASSWORD,
                                   host=POSTGRES_HOST, db=POSTGRES_DB))
    Base.metadata.create_all(engine)


def dropall(table_name):
    engine = create_engine('postgresql://{user}:{password}@{host}/{db}'
                           .format(user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                                   host=POSTGRES_HOST, db=POSTGRES_DB),
                           encoding='utf-8', echo=False)
    conn = engine.connect()
    conn.execute("DROP TABLE IF EXISTS "+table_name+";")


def getall(table_name):
    conn = psycopg2.connect('postgresql://{user}:{password}@{host}/{db}'
                              .format(user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                                      host=POSTGRES_HOST, db=POSTGRES_DB))
    cur = conn.cursor()
    cur.execute("SELECT * FROM "+table_name)
    col_name = [description[0] for description in cur.description]
    all_data = []
    for each in cur:
        all_data.append(each)
    df = pd.DataFrame(all_data, columns=col_name)
    return df


class InteractDB:
    def __init__(self):
        self.session = connect_db()

    def get_price_list(self, symbols):
        one_day = timedelta(days=1)
        price_list = []
        date_list = []
        for i, symbol in enumerate(symbols):
            print(symbol)
            day = START
            price_list_temp = []
            j = 0
            while True:
                day += one_day
                price = self._get_price(symbol, day)
                if price and j==0:
                    first_price = price
                    j += 1
                price_list_temp.append(price)
                if i == 0:
                    date_list.append(day)
                if day >= END:
                    break
            price_list_temp =\
                [(price-first_price)/first_price \
                    if price else price \
                        for price in price_list_temp]
            price_list.append(price_list_temp)
        return date_list, price_list

    def _get_price_list(self, symbols):
        n_symbols = len(symbols)
        one_day = timedelta(days=1)
        price_list = []
        date_list = []
        filters =[]
        for symbol in symbols:
            filters.append([StockPrice.ticker_symbol==symbol])

        day = START
        while True:
            day += one_day
            date_list.append(day)
            sps = self.session.query(StockPrice).\
                filter(StockPrice.date==day).\
                    filter(StockPrice.ticker_symbol.in_(filters)).all()
            # sps = sps.order_by(StockPrice.ticker_symbol).all()
            price_list_temp = [sp.price for sp in sps]
            price_list.append(price_list_temp)
            if day >= END:
                break
        
        first_price_list = [[0]*n_symbols]
        while True:
            for price_list_temp in price_list:
                for i, (first_price, price) in \
                    enumerate(zip(first_price_list, price_list_temp)):
                    if not first_price and price:
                        first_price_list[i] = price

                if all(first_price_list):
                    break
        symbols = [sp.ticker_symbol for sp in sps]
        price_array = np.array(price_list).T
        price_list = price_array.tolist()
        return date_list, price_list, symbols

    def get_symbols(self):
        tss = self.session.query(TickerSymbol).\
            order_by(TickerSymbol.name).all()
        symbols = []
        for ts in tss:
            sp = self.session.query(StockPrice).\
                filter(StockPrice.ticker_symbol==ts.name).\
                    order_by(asc('date')).first()
            if not sp:
                continue
            if sp.date <= START and sp.price:
                symbols.append(ts.name)

        symbols = symbols[:100]
        print('symbols=', symbols)
        return symbols

    def _get_price(self, symbol, date):
        instance = self.session.query(StockPrice).\
            filter(StockPrice.date==date).\
                filter(StockPrice.ticker_symbol==symbol).first()
        if instance:
            price = instance.price
            return price
        else:
            return
