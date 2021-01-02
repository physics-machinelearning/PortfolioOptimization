from datetime import datetime
from datetime import timedelta

START = datetime(
    year=2020,
    month=1,
    day=1
)
END = datetime.now().today()

START_PARSE = datetime.now() - timedelta(days=1)
