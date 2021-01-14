import matplotlib.pyplot as plt
import numpy as np

from optimization import CalcParam, cvxopt_qp_solver
from backtest import BackTest
from db_tools import InteractDB
from config import logger


if __name__ == '__main__':
    idb = InteractDB()
    symbols = idb.get_symbols()
    date_list, price_list = idb.get_price_list(symbols)
    cp = CalcParam()
    mean = cp.calc_expected_r(symbols, price_list)
    cov_df = cp.calc_cov(symbols, price_list)
    r = mean.values
    r_e = 0.2
    cov = cov_df.values
    sol = cvxopt_qp_solver(r, r_e, cov)
    x_opt = np.array(sol['x'])
    logger.info('x_opt: {}'.format(x_opt))
    logger.info("Variance (x_opt): {}".format(sol["primal objective"]))
