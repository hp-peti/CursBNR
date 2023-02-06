import datetime as dt
from typing import Iterable, List, Tuple

_DateT = str | dt.date | dt.datetime
_NumT = str | int | float

Date = dt.date
Numeric = int | float
DateTime = dt.datetime


def to_date(date: _DateT) -> Date:
    if isinstance(date, str):
        return dt.date.fromisoformat(date)
    elif isinstance(date, dt.datetime):
        return date.date()
    else:
        assert isinstance(date, dt.date)
        return date


def to_numeric(x: _NumT) -> Numeric:
    if isinstance(x, int):
        return x
    f = float(x) if not isinstance(x, float) else x
    i = int(f)
    return f if i != f else i


def to_datetime(date: _DateT) -> DateTime:
    if isinstance(date, str):
        return dt.datetime.fromisoformat(date)
    elif isinstance(date, dt.date):
        return dt.datetime.combine(date, dt.time())
    else:
        assert isinstance(date, dt.datetime)
        return date


def extract_dates_values(
    rows: Iterable[Tuple[Date, str, Numeric]], /, *, currency: str
) -> Tuple[List[Date], List[Numeric]]:

    if currency is not None:
        rows = filter(lambda dcv: dcv[1] == currency, rows)

    rows = map(lambda dcv: (dcv[0], dcv[2]), rows)

    *dates_values, = zip(*rows)
    if not len(dates_values):
        return list(), list()

    dates, values = dates_values
    return list(dates), list(values)


class CursMap(dict):
    def __init__(self):
        pass

    def put_value(self, date: _DateT, currency: str, value: _NumT):
        assert isinstance(currency, str)
        submap = self.get(currency, None)
        if submap is None:
            self[currency] = (submap := dict())
        submap[to_date(date)] = to_numeric(value)

    def get_value(self, date: _DateT, currency: str) -> Numeric | None:
        assert isinstance(currency, str)
        submap = self.get(currency, None)
        if submap is not None:
            return submap.get(currency, None)

    def rows(self) -> Iterable[Tuple[str, Date, Numeric]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                yield date, currency, value

    def get_size(self):
        return sum(len(submap) for submap in self.values())
