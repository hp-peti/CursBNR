from typing import List, Tuple
from suds.client import Client as _suds_Client
from datetime import datetime


class CursClient:
    def __init__(self):
        self._client = _suds_Client("http://www.infovalutar.ro/curs.asmx?wsdl")

    @property
    def lastdate(self) -> datetime:
        return self._client.service.lastdateinserted()

    def getall(self, date: datetime | None = None) -> List[Tuple[datetime, str, int | float]]:
        if date is None:
            date = self.lastdate
        assert isinstance(date, datetime)
        currencies = self._client.service.getall(date).diffgram[0][0][0][0]

        def number(x: str) -> int | float:
            f = float(x)
            i = int(f)
            return f if i != f else i

        return [
            (date, str(currency.IDMoneda[0]), number(currency.Value[0])) for currency in currencies
        ]
