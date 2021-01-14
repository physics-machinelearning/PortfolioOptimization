import argparse

import pandas as pd
import pandas_datareader.data as pdr

from models import StockPrice, TickerSymbol
from db_tools import connect_db
from config import START, START_PARSE, END, logger

SOURCE_DICT = {
    'NASDAQ': 'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt'
}


class TickerSymbolParser:
    def __init__(self):
        self.session = connect_db()

    def insert_db(self):
        for market, url in SOURCE_DICT.items():
            df = self._parse(url)
            for index, row in df.iterrows():
                symbol = row['Symbol']
                security_name = row['Security Name']
                if not len(self.session.query(TickerSymbol)
                   .filter(TickerSymbol.name == symbol).all()):
                    ts = TickerSymbol(
                        market=market,
                        security_name=security_name,
                        name=symbol
                    )
                    self.session.add(ts)
                else:
                    print('already exist', symbol)
            self.session.commit()
        self.session.close()

    def _parse(self, url):
        df = pd.read_csv(url, sep='|')
        df = df[df['Financial Status'] == 'N']
        df = df[df['Test Issue'] == 'N']
        df = df[df['ETF'] == 'N']
        cols = ['Symbol', 'Security Name']
        df = df[cols]
        return df


class StockPriceParser:
    def __init__(self):
        self.session = connect_db()

    def insert_db(self, start, end):
        logger.debug('StockPriceParser.insert_db')
        ts_all = self.session.query(TickerSymbol).all()
        for ts in ts_all:
            symbol = ts.name
            logger.debug(symbol)
            try:
                df = pdr.DataReader(
                    symbol, 'yahoo', start, end
                )
                self._insert(symbol, df)
            except KeyError as err:
                logger.error(err)
        self.session.close()

    def _insert(self, symbol, df):
        for date, row in df.iterrows():
            date = date.to_pydatetime()
            price = row['High']
            sp = StockPrice(
                ticker_symbol=symbol,
                date=date,
                price=price
            )
            already_exist = self.session.query(StockPrice)\
                .filter(StockPrice.ticker_symbol == symbol)\
                .filter(StockPrice.date == date)\
                .filter(StockPrice.price == price).all()
            if not len(already_exist):
                self.session.add(sp)
            else:
                print('already exists', symbol, date)
        self.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('arg1')
    args = parser.parse_args()

    if args.arg1 == 'ticker':
        tsp = TickerSymbolParser()
        tsp.insert_db()
    elif args.arg1 == 'stock_all':
        spp = StockPriceParser()
        spp.insert_db(START, END)
    elif args.arg1 == 'stock_today':
        spp = StockPriceParser()
        spp.insert_db(START_PARSE, END)
