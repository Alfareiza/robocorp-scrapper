from datetime import date

from datetime import datetime, timedelta
from typing import Tuple

from dateutil.relativedelta import relativedelta


def parse_string_date(datetime_str):
    now = datetime.now()

    if 'mins ago' in datetime_str:
        minutes = int(datetime_str.split()[0])
        return now - timedelta(minutes=minutes)

    if 'hours ago' in datetime_str:
        hours = int(datetime_str.split()[0])
        return now - timedelta(hours=hours)

    if 'yesterday' in datetime_str:
        return now - timedelta(days=1)

    try:
        month_day = datetime.strptime(datetime_str, '%B %d')
        return month_day.replace(year=now.year)
    except ValueError:
        pass

    try:
        return datetime.strptime(datetime_str, '%B %d, %Y')
    except ValueError as e:
        raise ValueError(f"Unrecognized time string format: {datetime_str}") from e


def get_month_date(months_back: int) -> tuple[date, date]:
    """
    >>> get_month_date(0)
    (datetime.date(2024, 8, 1), datetime.date(2024, 8, 31))
    >>> get_month_date(1)
    (datetime.date(2024, 8, 1), datetime.date(2024, 8, 31))
    >>> get_month_date(2)
    (datetime.date(2024, 7, 1), datetime.date(2024, 7, 31))
    >>> get_month_date(3)
    (datetime.date(2024, 6, 1), datetime.date(2024, 6, 30))
    """
    today = datetime.now()
    target_date = today if months_back in {0, 1} else today - relativedelta(months=(months_back - 1))
    first_day_of_month = date(target_date.year, target_date.month, 1)
    return first_day_of_month, today


def get_last_day_of_month(d: date) -> date:
    """
    >>> get_last_day_of_month(date(2024, 8, 1))
    datetime.date(2024, 8, 31)
    >>> get_last_day_of_month(date(2024, 2, 1))
    datetime.date(2024, 2, 29)
    """
    first_day_next_month = (d + relativedelta(day=31)).replace(day=1) + relativedelta(months=1)
    return first_day_next_month - relativedelta(days=1)


def is_datetime_in_interval(input_datetime: datetime, start: date, end: date) -> bool:
    """
    >>> is_datetime_in_interval(datetime.now(), date(2024, 7, 1), date(2024, 7, 31))
    False
    """
    start_datetime = datetime.combine(start, datetime.min.time())
    end_datetime = datetime.combine(end, datetime.max.time())
    return start_datetime <= input_datetime <= end_datetime
