import sqlite3
from datetime import datetime, date as _date, time as _time
from typing import Sequence
import datetime as dt

from curstypes import _DateT, to_date

class CursDB:
    def __init__(self, dbname: str):
        self._db = sqlite3.connect(
            dbname, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
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

    def put_value(
        self,
        date: _DateT,
        currency: str,
        value: int | float,
    ):
        return self.insert_value(date, currency, value, replace=True)

    def insert_value(
        self,
        date: _DateT,
        currency: str,
        value: int | float,
        *,
        replace: bool | None = None,
        commit: bool = False,
    ):
        date = to_date(date)
        assert isinstance(currency, str)
        assert isinstance(value, (int, float))
        _or_action = {None: "", True: "OR REPLACE", False: "OR IGNORE"}[replace]
        cursor = self._db.execute(
            "INSERT " + _or_action + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date, currency, value),
        )
        cursor.close()

    def commit(self):
        self._db.commit()

    def rollback(self):
        self._db.rollback()

    def get_value(self, date: _DateT, currency: str) -> int | float | None:
        date = to_date(date)
        assert isinstance(currency, str)
        cursor = self._db.execute(
            "SELECT value FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date, currency],
        )
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]

    def remove_value(self, date: _DateT, currency: str):
        date = to_date(date)
        assert isinstance(currency, str)
        cursor = self._db.execute(
            "DELETE FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date.date(), currency],
        )
        result = cursor.fetchone()
        cursor.close()

    def select_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> Sequence[tuple[datetime, str, int | float]]:
        sql = "SELECT date, currency, value FROM CURSBNR"
        params = []
        sep = "\nWHERE "
        _AND_ = " AND "

        def is_str(x):
            return isinstance(x, str)

        if date is None:
            pass
        elif isinstance(date, (tuple, list)):
            d1, d2 = date

            if d1 is not None:
                sql += sep + "date >= ?"
                params.append(to_date(d1))
                sep = _AND_

            if d2 is not None:
                sql += sep + "dat <= ?"
                params.append(to_date(d2))
                sep = _AND_

        else:
            sql += sep + "date=?"
            params.append(to_date(date))
            sep = _AND_

        if currency is None:
            pass

        elif isinstance(currency, list):
            sql += sep + "currency in (" + ", ".join(["?"] * len(currency)) + ")"
            assert all(map(is_str, currency))
            params.extend(currency)
            sep = _AND_
        else:
            assert is_str(currency)
            sql += sep + "currency = ?"
            params.append(currency)
            sep = _AND_

        def map_order(order):
            return {
                "currency": "currency",
                "date": "date",
                "currency:desc": "currency DESC",
                "date:desc": "date DESC",
                "currency:asc": "currency ASC",
                "date:asc": "date ASC",
            }[order]

        if orderby is None:
            orderby = []
        elif isinstance(orderby, (tuple, list)):
            orderby = list(map(map_order, orderby))
        else:
            orderby = [map_order(orderby)]
        if orderby:
            sql += " ORDER BY\n    " + ",".join(orderby)

        #print(sql)
        cursor = self._db.execute(sql, params)
        try:
            while (row := cursor.fetchone()) is not None:
                date, currency, value = row
                yield date, currency, value
        finally:
            cursor.close()

    def close(self):
        self._db.close()
