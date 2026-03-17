from datetime import date
from dateutil.relativedelta import relativedelta

def default_date_range() -> tuple[date, date]:
    return date.today() - relativedelta(months=3), date.today()