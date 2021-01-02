from datetime import timedelta, datetime
import numpy as np
import pandas as pd
import cvxopt

from models import StockPrice, TickerSymbol
from db_tools import connect_db
from stock_parser import START, END
from db_tools import InteractDB


class CalcParam:
    def __init__(self):
        self.session = connect_db()

    def calc_cov(self):
        symbols = self._get_symbols()
        n_symbols = len(symbols)
        cov = np.zeros((n_symbols, n_symbols))
        for i in range(n_symbols):
            for j in range(i):
                symbol1 = symbols[i]
                symbol2 = symbols[j]
                print(symbol1, symbol2)
                cov2 = self._calc_cov2(symbol1, symbol2)
                if all(cov2.shape):
                    cov[i, j] = cov2[0, 1]
                    cov[j, i] = cov2[0, 1]
                    cov[i, i] = cov2[0, 0]
                    cov[j, j] = cov2[1, 1]
                else:
                    cov[i, j] = np.nan
                    cov[j, i] = np.nan
                    cov[i, i] = np.nan
                    cov[j, j] = np.nan
        df_cov = pd.DataFrame(cov, columns=symbols, index=symbols)
        return df_cov

    def calc_expected_r(self, symbols, price_list):
        price_array = np.array(price_list).T
        df = pd.DataFrame(price_array)
        mean = df.mean().values.flatten()
        mean_df = pd.DataFrame(mean, index=symbols)
        return mean_df

    def _calc_cov2(self, symbol1, symbol2):
        one_day = timedelta(days=1)
        day = START
        price_list = []
        i = 0
        while True:
            day += one_day
            first = self.session.query(StockPrice).\
                filter(StockPrice.date==day).\
                    filter(StockPrice.ticker_symbol==symbol1).first()
            second = self.session.query(StockPrice).\
                filter(StockPrice.date==day).\
                    filter(StockPrice.ticker_symbol==symbol2).first()
            if first and second:
                if i == 0:
                    first_price1 = first.price
                    first_price2 = second.price
                else:
                    price1 = first.price - first_price1
                    price1 /= first_price1
                    price2 = second.price - first_price2
                    price2 /= first_price2
                    price_list.append([price1, price2])
                i += 1
            if day > END:
                break
        cols = [symbol1, symbol2]
        df = pd.DataFrame(price_list, columns=cols)
        cov = df.cov().values
        return cov

    def _calc_cov(self, symbols, price_list):
        n_symbols = len(symbols)
        cov = np.zeros((n_symbols, n_symbols))
        
        price_array = np.array(price_list).T
        df_price = pd.DataFrame(price_array, columns=symbols)
        df_price = df_price.astype(float)
        df_cov = df_price.cov()
        return df_cov


def cvxopt_qp_solver(r, r_e, cov):
    n = len(r)
    r = cvxopt.matrix(r)

    P = cvxopt.matrix(2.0 * np.array(cov))
    q = cvxopt.matrix(np.zeros((n, 1)))
    G = cvxopt.matrix(np.concatenate((-np.transpose(r), -np.identity(n)), 0))
    h = cvxopt.matrix(np.concatenate((-np.ones((1,1)) * r_e, np.zeros((n,1))), 0))
    A = cvxopt.matrix(1.0, (1, n))
    b = cvxopt.matrix(1.0)    
    sol = cvxopt.solvers.qp(P, q, G, h, A, b)
    return sol


if __name__ == '__main__':
    cp = CalcParam()
    mean = cp.calc_expected_r()
    print(mean)
    cov = cp.calc_cov()
    print(cov)
    r = mean.values
    r_e = 0.005
    cov = cov.values
    sol = cvxopt_qp_solver(r, r_e, cov)
    x_opt = np.array(sol['x'])
    print(x_opt)
    print("Variance (x_opt) :", sol["primal objective"])