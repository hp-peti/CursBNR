import sqlite3
from datetime import datetime, date as _date, time as _time
from typing import Any, List, Literal, Sequence
import datetime as dt

from curstypes import _DateT, to_date, to_date_opt, Date, Numeric

from pathlib import Path


class CursDB:
    DB_MODES = "ro", "rw", "rwc"

    def __init__(
        self,
        dbname: str | Path,
        mode: Literal["ro", "rw", "rwc"] | None = None,
    ):
        if not isinstance(dbname, Path):
            dbname = Path(dbname)

        dbname = dbname.absolute().as_uri()

        if mode is not None:
            assert mode in self.DB_MODES
            dbname += f"?mode={mode}"
            self._read_only = mode in ("ro",)

        # print(dbname)
        self._db = sqlite3.connect(
            dbname,
            uri=True,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )

        db = self._db
        cursor = db.execute(
            "SELECT COUNT(*)\nFROM sqlite_schema\nWHERE name == ?",
            ("CURSBNR",),
        )

        try:
            has_table = cursor.fetchone()[0]
        finally:
            cursor.close()

        if not has_table and not self._read_only:
            db.execute(
                """
                CREATE TABLE CURSBNR(
                    date DATE NOT NULL,
                    currency TEXT NOT NULL,
                    value NUMERIC NOT NULL,
                    PRIMARY KEY (date, currency)
                ) WITHOUT ROWID
                """
            ).close()

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
        self._db.execute(
            "INSERT "
            + _or_action
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date, currency, value),
        ).close()

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
        try:
            result = cursor.fetchone()
        finally:
            cursor.close()

        if result is not None:
            return result[0]

    def remove_value(self, date: _DateT, currency: str):
        date = to_date(date)
        assert isinstance(currency, str)
        self._db.execute(
            "DELETE FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date.date(), currency],
        ).close()

    def get_currencies(self) -> List[str]:
        cursor = self._db.execute("SELECT currency FROM CURSBNR GROUP BY currency")
        try:
            return [currency for currency, in cursor.fetchall()]
        finally:
            cursor.close()

    def get_date_range(self, currency=None) -> tuple[Date | None, Date | None]:
        def is_str(x):
            return isinstance(x, str)

        sql = "SELECT MIN(date), MAX(date) FROM CURSBNR"
        sep = "\nWHERE "
        _AND_ = " AND "
        params = []

        if currency is None:
            pass

        elif isinstance(currency, (list, set, tuple)):
            assert all(map(is_str, currency))
            sql += sep + "currency in (" + ", ".join(["?"] * len(currency)) + ")"
            params.extend(currency)
            sep = _AND_

        else:
            assert is_str(currency)
            sql += sep + "currency = ?"
            params.append(currency)
            sep = _AND_

        mind, maxd = self._exec_fetchone(sql, params)
        return to_date_opt(mind), to_date_opt(maxd)

    def select_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> List[tuple[Date, str, Numeric]]:
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
                sql += sep + "date <= ?"
                params.append(to_date(d2))
                sep = _AND_

        else:
            sql += sep + "date=?"
            params.append(to_date(date))
            sep = _AND_

        if currency is None:
            pass

        elif isinstance(currency, (list, set, tuple)):
            assert all(map(is_str, currency))
            sql += sep + "currency in (" + ", ".join(["?"] * len(currency)) + ")"
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

        if orderby is not None:
            if isinstance(orderby, str):
                orderby = orderby.split(",")
            orderby = list(map(map_order, orderby))

        if orderby:
            sql += " ORDER BY\n    " + ",".join(orderby)

        # print(sql)
        return self._exec_fetchall(sql, params)

    def close(self):
        self._db.close()

    def _exec_fetchall(self, sql: str, params: list = []) -> list:
        cursor = self._db.execute(sql, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def _exec(self, sql: str, params: list = []) -> None:
        self._db.execute(sql, params).close()

    def _exec_fetchone(self, sql: str, params: list = []) -> Any:
        cursor = self._db.execute(sql, params)
        try:
            return cursor.fetchone()
        finally:
            cursor.close()
