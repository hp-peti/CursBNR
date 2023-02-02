import sqlite3
from datetime import datetime, date as _date, time as _time
from typing import Sequence


class CursDB:
    def __init__(self):
        self._db = sqlite3.connect(
            "curs.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )

        db = self._db
        has_table = db.execute(
            """
            SELECT COUNT(*) FROM sqlite_schema WHERE name == 'CURSBNR'
        """
        ).fetchall()[0][0]
        if not has_table:
            cursor = db.execute(
                """
                CREATE TABLE CURSBNR(
                    date DATE NOT NULL,
                    currency TEXT NOT NULL,
                    value NUMERIC NOT NULL,
                    PRIMARY KEY (date, currency)
                ) WITHOUT ROWID
                """
            )
            cursor.close()

    def put_value(self, date: datetime, currency: str, value: int | float):
        assert isinstance(date, datetime)
        assert isinstance(currency, str)
        assert isinstance(value, (int, float))
        cursor = self._db.execute(
            "INSERT OR REPLACE INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date.date(), currency.upper(), value),
        )
        cursor.close()

    def commit(self):
        self._db.commit()

    def rollback(self):
        self._db.rollback()

    def get_value(self, date: datetime, currency: str) -> int | float | None:
        assert isinstance(date, datetime)
        assert isinstance(currency, str)
        cursor = self._db.execute(
            "SELECT value FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date.date(), currency.upper()],
        )
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]

    def remove_value(self, date: datetime, currency: str):
        assert isinstance(date, datetime)
        assert isinstance(currency, str)
        cursor = self._db.execute(
            "DELETE FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date.date(), currency.upper()],
        )
        result = cursor.fetchone()
        cursor.close()

    def select_rows(
        self,
        *,
        date: datetime | tuple[datetime, datetime] | None = None,
        currency: str | list[str] | None = None,
    ) -> Sequence[tuple[datetime, str, int | float]]:
        sql = "SELECT date, currency, value FROM CURSBNR"
        params = []
        sep = "\nWHERE "
        if isinstance(date, datetime):
            sql += sep + "date=?"
            params += date.date()
            sep = " AND "
        elif isinstance(date, tuple):
            d1, d2 = date
            sql += sep + "date >= ? AND date <= ?"
            params += [d1.date(), d2.date()]
            sep = " AND "
        else:
            assert date is None

        if isinstance(currency, str):
            sql += sep + "currency = ?"
            params += [currency.upper()]
            sep = " AND "
        elif isinstance(currency, list):
            sql += sep + "currency in (" + ", ".join(["?"] * len(currency)) + ")"
            params += [c.upper() for c in currency]
            sep = " AND "
        else:
            assert currency is None

        def extend(date: _date) -> datetime:
            return datetime.combine(date, _time())

        cursor = self._db.execute(sql, params)
        try:
            while (row := cursor.fetchone()) is not None:
                date, currency, value = row
                yield extend(date), currency, value
        finally:
            cursor.close()

    def close(self):
        self._db.close()
