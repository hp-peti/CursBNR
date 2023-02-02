from typing import List, Tuple
from suds.client import Client as _suds_Client

import datetime as dt

_Date = str | dt.date | dt.datetime

def date2dt(date: _Date) -> dt.datetime:
    if isinstance(date, str):
        return dt.datetime.fromisoformat(date)
    elif isinstance(date, dt.date):
        return dt.datetime.combine(date, dt.time())
    else:
        assert isinstance(date, dt.datetime)
        return date

class CursClient:
    def __init__(self):
        self._client = _suds_Client("http://www.infovalutar.ro/curs.asmx?wsdl")

    @property
    def lastdate(self) -> dt.date:
        return self._client.service.lastdateinserted().date()

    def getall(self, date: _Date | None = None) -> List[Tuple[dt.date, str, int | float]]:
        if date is None:
            date = self.lastdate
        date = date2dt(date)

        level0 = self._client.service.getall(date).diffgram
        level1 = level0[0] if level0 else []
        level2 = level1[0] if level1 else []
        level3 = level2[0] if level2 else []
        currencies = level3[0] if len(level3) else []

        def number(x: str) -> int | float:
            f = float(x)
            i = int(f)
            return f if i != f else i

        return [
            (date.date(), str(currency.IDMoneda[0]), number(currency.Value[0])) for currency in currencies
        ]

    def getvalue(self, date: _Date, currency: str) -> int | float | None:
        return self._client.service.getvalue(date, currency)
