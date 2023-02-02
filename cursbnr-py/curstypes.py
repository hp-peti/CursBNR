import datetime as dt
from typing import Tuple, Sequence

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

class CursMap(dict):
    def __init__(self):
        pass

    def put_value(self, date: _DateT, currency: str, value: _NumT):
        submap = self.get(currency, None)
        assert isinstance(currency, str)
        if submap is None:
            self[currency] = (submap := dict())
        submap[to_date(date)] = to_numeric(value)

    def get_value(self, date: _DateT, currency: str) -> Numeric | None:
        assert isinstance(currency, str)
        submap = self.get(currency, None)
        if submap is not None:
            return submap.get(currency, None)

    def rows(self) -> Sequence[Tuple[str, Date, Numeric]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                yield date, currency, value
