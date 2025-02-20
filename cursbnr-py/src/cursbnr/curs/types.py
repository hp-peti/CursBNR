import datetime as dt
from collections.abc import Iterable
from typing import Any, NamedTuple, TypeAliasType, overload

type _DateT = str | dt.date | dt.datetime
type _NumT = str | int | float

type Date = dt.date
type Numeric = int | float
type DateTime = dt.datetime


class DateCurrencyRow(NamedTuple):
    date: Date
    currency: str


class DateCurrencyValueRow(NamedTuple):
    date: Date
    currency: str
    value: Numeric


class DateCurrencyOptValueRow(NamedTuple):
    date: Date
    currency: str
    value: Numeric | None


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


@overload
def _require_[_T](_type: type[_T], _val) -> _T: ...


@overload
def _require_(_type: TypeAliasType, _val) -> Any: ...


def _require_(_type: type | TypeAliasType, _val) -> Any:
    if isinstance(_type, TypeAliasType):
        _type = _type.__value__
    if not isinstance(_val, _type):  # type: ignore
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
    rows: Iterable[DateCurrencyOptValueRow], /, *, currency: str
) -> tuple[list[Date], list[Numeric]]:
    _rows: Iterable[Any] = rows
    if currency is not None:
        _rows = filter(lambda dcv: dcv[1] == currency, _rows)
    _rows = map(lambda dcv: (dcv[0], dcv[2]), _rows)

    dates, values = list(), list()
    for date, value in _rows:
        dates.append(date)
        values.append(value)

    return dates, values


class CursMap(dict[str, dict[Date, Numeric | None]]):
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
        submap = self.get(currency)
        if submap is not None:
            return submap.get(to_date(date))
        return None

    def rows(self) -> Iterable[tuple[Date, str, Numeric]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                if value is not None:
                    yield date, currency, value

    def all_rows(self) -> Iterable[tuple[Date, str, Numeric | None]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                yield date, currency, value

    def no_value_rows(self) -> Iterable[tuple[Date, str]]:
        for currency, rates in self.items():
            for date, value in rates.items():
                if value is None:
                    yield date, currency

    def get_size(self):
        return sum(len(submap) for submap in self.values())
