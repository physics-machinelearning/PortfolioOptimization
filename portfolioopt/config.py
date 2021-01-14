from datetime import datetime
from datetime import timedelta
import logging


START = datetime(
    year=2020,
    month=1,
    day=2
)
END = datetime.now().today()

START_PARSE = datetime.now() - timedelta(days=1)


formatter = '%(levelname)s : %(asctime)s : %(message)s'

logging.basicConfig(level=logging.DEBUG, format=formatter, filename='portfolioopt.log')

logger = logging.getLogger(__name__)