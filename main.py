import matplotlib.pyplot as plt
import numpy as np

from optimization import CalcParam, cvxopt_qp_solver
from backtest import BackTest
from db_tools import InteractDB
from config import logger

if __name__ == '__main__':
    idb = InteractDB()
    symbols = idb.get_symbols()
    # date_list, price_list, symbols = idb._get_price_list(symbols)
    date_list, price_list = idb.get_price_list(symbols)
    cp = CalcParam()
    mean = cp.calc_expected_r(symbols, price_list)
    logger.info('mean=', mean)
    cov_df = cp._calc_cov(symbols, price_list)
    logger.info('cov_df', cov_df)
    r = mean.values
    r_e = 0.2
    cov = cov_df.values
    sol = cvxopt_qp_solver(r, r_e, cov)
    x_opt = np.array(sol['x'])
    logger.info('x_opt', x_opt)
    logger.info("Variance (x_opt) :", sol["primal objective"])

    bt = BackTest(cov_df.index, x_opt.flatten())
    logger.info('complete bt.get_price_list()')
    portfolio_price_list = bt.get_portfolio_price_list(price_list)
    logger.info('complete portfolio_price_list')

    plt.figure()
    for price in price_list:
        plt.plot(date_list, price)

    plt.plot(date_list, portfolio_price_list, linewidth=5)
    plt.show()
