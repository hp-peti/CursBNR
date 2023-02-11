import datetime as dt
from typing import Any, Iterable, List, Tuple, Type, TypeVar

from typing import NamedTuple

_DateT = str | dt.date | dt.datetime
_NumT = str | int | float

Date = dt.date
Numeric = int | float
DateTime = dt.datetime

ValueRow = NamedTuple("ValueRow", date=Date, currency=str, value=Numeric)
OptValueRow = NamedTuple("OptValueRow",date=Date, currency=str, value=Numeric|None)
NoValueRow = NamedTuple("NoValueRow", date=Date, currency=str)

def to_date_opt(date: _DateT | None) -> Date | None:
    if date is None or date == "":
        return None
    return to_date(date)


def to_date(date: _DateT) -> Date:
    if isinstance(date, str):
        return dt.date.fromisoformat(date)
    elif isinstance(date, dt.datetime):
        return date.date()
    else:
        return require_date(date)

_T = TypeVar("_T")

def _require_(_type: Type[_T], _val) -> _T:
    if not isinstance(_val, _type):
        raise TypeError(f"{_val}: expected {_type}, got {type(_val)}")
    return _val

def require_date(date) -> Date:
    return _require_(Date, date)

def require_datetime(datetime) -> DateTime:
    return _require_(DateTime, datetime)

def require_str(s) -> str:
    return _require_(str, s)

def to_numeric_opt(x: _NumT | None) -> Numeric | None:
    if x is None:
        return None
    return to_numeric(x)

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
    rows: Iterable[OptValueRow], /, *, currency: str
) -> Tuple[List[Date], List[Numeric]]:

    if currency is not None:
        rows = filter(lambda dcv: dcv[1] == currency, rows)

    rows = map(lambda dcv: (dcv[0], dcv[2]), rows)

    dates, values = list(), list()
    for date, value in rows:
        dates.append(date)
        values.append(value)

    return dates, values

class CursMap(dict):
    def __init__(self):
        pass

    def put_value(self, date: _DateT, currency: str, value: _NumT | None):
        assert isinstance(currency, str)
        submap = self.get(currency, None)
        if submap is None:
            submap = dict()
            self[currency] = submap
        submap[to_date(date)] = to_numeric_opt(value)

    def get_value(self, date: _DateT, currency: str) -> Numeric | None:
        assert isinstance(currency, str)
        submap = self.get(currency, None)
        if submap is not None:
            return submap.get(currency, None)

    def rows(self) -> Iterable[Tuple[str, Date, Numeric]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                if value is not None:
                    yield date, currency, value

    def all_rows(self) -> Iterable[Tuple[Date, str, Numeric|None]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                yield date, currency, value

    def no_value_rows(self) -> Iterable[Tuple[Date, str]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                if value is None:
                    yield date, currency


    def get_size(self):
        return sum(len(submap) for submap in self.values())
