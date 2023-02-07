import sqlite3
from datetime import datetime, date as _date, time as _time
from typing import Any, List, Literal 
import datetime as dt

from curstypes import _DateT, _NumT, to_date, to_date_opt, Date, Numeric, to_numeric

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

        if not self._has_table("CURSBNR") and not self._read_only:
            self._create_main_table()

        if not self._has_table("CURSBNR_NO_VALUE") and not self._read_only:
            self._create_no_value_table()

    def _has_table(self, tablename: str):
        return self._exec_fetchone(
            "SELECT COUNT(*)\nFROM sqlite_schema\nWHERE name == ?",
            (tablename,),
        )[0] > 0


    def close(self):
        self._db.close()

    def commit(self):
        self._db.commit()

    def rollback(self):
        self._db.rollback()

    def get_currencies(self) -> list[str]:
        rows = self._exec_fetchall("SELECT currency FROM CURSBNR GROUP BY currency")
        return [currency for (currency,) in rows]

    def get_date_range(self, currency=None) -> tuple[Date | None, Date | None]:
        def is_str(x):
            return isinstance(x, str)

        sql, params = self._sql_where("SELECT MIN(date), MAX(date) FROM CURSBNR", currency=currency)

        mind, maxd = self._exec_fetchone(sql, params)
        return to_date_opt(mind), to_date_opt(maxd)

    def put_value(
        self,
        date: _DateT,
        currency: str,
        value: _NumT | None,
    ):
        if value is not None:
            self.insert_value(date, currency, value, replace=True)
            self.unset_no_value(date, currency)
        else:
            self.set_no_value(date, currency)
            self.remove_rows(date, currency)

    def insert_value(
        self,
        date: _DateT,
        currency: str,
        value: _NumT,
        *,
        replace: bool | None = None,
    ):
        date = to_date(date)
        assert isinstance(currency, str)
        value = to_numeric(value)
        _or_action = {None: "", True: "OR REPLACE", False: "OR IGNORE"}[replace]
        self._exec(
            "INSERT "
            + _or_action
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date, currency, value),
        )


    def get_value(self, date: _DateT, currency: str) -> Numeric | None:
        date = to_date(date)
        assert isinstance(currency, str)
        result = self._exec_fetchone(
            "SELECT value FROM CURSBNR WHERE date=? AND CURRENCY=?",
            [date, currency],
        )
        if result is not None:
            return result[0]


    def remove_rows(
        self,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
    ):
        sql, params = self._sql_where("DELETE FROM CURSBNR", date=date, currency=currency)

        self._exec(sql, params)

 
    def select_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> list[tuple[Date, str, Numeric]]:

        sql, params = self._sql_where(
            "SELECT date, currency, value FROM CURSBNR", date=date, currency=currency
        )

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
            sql += "\nORDER BY\n    " + ",".join(orderby)

        # print(sql, params)
        return self._exec_fetchall(sql, params)

    def has_no_value(self, date: _DateT, currency: str) -> bool:
        date = to_date(date)
        assert isinstance(currency, str)
        result = self._exec_fetchone(
            "SELECT COUNT(*) FROM CURSBNR_NO_VALUE WHERE date=? AND CURRENCY=?",
            [date, currency],
        )
        return bool(result[0])

    def set_no_value(
        self,
        date: _DateT,
        currency: str,
    ):
        date = to_date(date)
        assert isinstance(currency, str)

        self._exec(
            "INSERT OR IGNORE INTO CURSBNR_NO_VALUE (date, currency) VALUES (?, ?)",
            (date, currency),
        )

    def unset_no_value(
        self,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
    ):
        sql, params = self._sql_where("DELETE FROM CURSBNR_NO_VALUE", date=date, currency=currency)

        self._exec(sql, params)

    def select_no_value_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> list[tuple[Date, str]]:
        sql, params = self._sql_where(
            "SELECT date, currency FROM CURSBNR_NO_VALUE", date=date, currency=currency
        )

        return self._exec_fetchall(sql, params)

    # ---------

    def _create_main_table(self):
        self._exec(
            """
            CREATE TABLE CURSBNR(
                date DATE NOT NULL,
                currency TEXT NOT NULL,
                value NUMERIC NOT NULL,
                PRIMARY KEY (date, currency)
            ) WITHOUT ROWID
            """
        )

    def _create_no_value_table(self):
        self._exec(
            """
            CREATE TABLE CURSBNR_NO_VALUE(
                date DATE NOT NULL,
                currency TEXT NOT NULL,
                PRIMARY KEY (date, currency)
            ) WITHOUT ROWID
            """
        )

    # ---------

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

    @staticmethod
    def _sql_where(
        sql: str,
        params: list = [],
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
    ) -> tuple[str, list]:
        params = list(params)
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

        return sql, params
