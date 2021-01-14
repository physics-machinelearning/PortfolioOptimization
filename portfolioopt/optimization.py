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

    def calc_expected_r(self, symbols, price_list):
        price_array = np.array(price_list).T
        df = pd.DataFrame(price_array)
        mean = df.mean().values.flatten()
        mean_df = pd.DataFrame(mean, index=symbols)
        return mean_df

    def calc_cov(self, symbols, price_list):
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
