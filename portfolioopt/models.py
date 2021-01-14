from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import Integer, String, Float, DateTime

Base = declarative_base()


class StockPrice(Base):
    __tablename__ = 'stock_price'

    # ティッカーシンボル名と日付をユニークキーに
    __table_args__ = (UniqueConstraint("ticker_symbol", "date"), )

    id = Column(Integer, primary_key=True)

    # ティッカーシンボル名
    ticker_symbol = Column(String(20))

    # 日付
    date = Column(DateTime)

    # 株価
    price = Column(Float)


class TickerSymbol(Base):
    __tablename__ = 'ticker_symbol'

    # 証券取引所
    market = Column(String(20))

    # Security Name
    security_name = Column(String(500))

    # ティッカーシンボル名
    name = Column(String(20), primary_key=True)
