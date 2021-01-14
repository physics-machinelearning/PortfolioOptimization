import matplotlib.pyplot as plt
import numpy as np

from potrfolioopt.optimization import CalcParam, cvxopt_qp_solver
from potrfolioopt.backtest import BackTest
from potrfolioopt.db_tools import InteractDB
from potrfolioopt.config import logger


if __name__ == '__main__':
    idb = InteractDB()
    symbols = idb.get_symbols()
    date_list, price_list = idb.get_price_list(symbols)
    cp = CalcParam()
    mean = cp.calc_expected_r(symbols, price_list)
    cov_df = cp._calc_cov(symbols, price_list)
    r = mean.values
    r_e = 0.2
    cov = cov_df.values
    sol = cvxopt_qp_solver(r, r_e, cov)
    x_opt = np.array(sol['x'])
    logger.info('x_opt: {}'.format(x_opt))
    logger.info("Variance (x_opt): {}".format(sol["primal objective"]))

    bt = BackTest(cov_df.index, x_opt.flatten())
    logger.info('complete bt.get_price_list()')
    portfolio_price_list = bt.get_portfolio_price_list(price_list)
    logger.info('complete portfolio_price_list')

    plt.figure()
    for price in price_list:
        plt.plot(date_list, price)

    plt.plot(date_list, portfolio_price_list, linewidth=5)
    plt.show()
