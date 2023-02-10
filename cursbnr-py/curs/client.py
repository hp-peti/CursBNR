from pathlib import Path
from typing import List, Tuple
from suds.client import Client as _suds_Client

import datetime as dt

from curs.types import _DateT, to_datetime, Date, to_date, Numeric, to_numeric


class CursClient:
    def __init__(self, use_local_wsdl: bool = False):
        url = "http://www.infovalutar.ro/curs.asmx?wsdl"
        if use_local_wsdl:
            url = (Path(__file__).resolve().parent / "curs.wsdl").as_uri()
        self._client = _suds_Client(url)

    @property
    def lastdate(self) -> dt.date:
        return self._client.service.lastdateinserted().date()

    def get_all(self, date: _DateT | None = None) -> List[Tuple[str, Numeric]]:
        if date is None:
            date = self.lastdate
        date = to_datetime(date)

        level0 = self._client.service.getall(date).diffgram
        level1 = level0[0] if level0 else []
        level2 = level1[0] if level1 else []
        level3 = level2[0] if level2 else []
        currencies = level3[0] if len(level3) else []

        return [
            (str(currency.IDMoneda[0]), to_numeric(currency.Value[0]))
            for currency in currencies
        ]

    def value(self, date: _DateT, currency: str) -> Numeric | None:
        return self._client.service.getvalue(date, currency)

    def get_value(self, date: _DateT, currency: str) -> Tuple[Date, str, Numeric]:
        result = self._client.service.getvalueadv(to_datetime(date), currency)
        return to_date(result.date), result.moneda, to_numeric(result.value)
