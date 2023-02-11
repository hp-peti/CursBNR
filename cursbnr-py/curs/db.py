from functools import partial
from itertools import starmap
import sqlite3
from datetime import datetime, date as _date, time as _time
from typing import Any, Callable, Iterable, Literal, NamedTuple, Type, TypeVar
import datetime as dt

from curs.types import (
    _DateT,
    _NumT,
    to_date,
    to_date_opt,
    Date,
    Numeric,
    to_numeric,
    require_str,
    ValueRow,
    NoValueRow,
)

from pathlib import Path

_OptValueRowT = tuple[_DateT, str, _NumT | None]
_ValueRowT = tuple[_DateT, str, _NumT]
_NoValueRowT = tuple[_DateT, str]
_OptOrNoValueRowT = _OptValueRowT | _NoValueRowT

_T = TypeVar("_T")
_NamedTuple_T = TypeVar("_NamedTuple_T", bound=NamedTuple)


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
            if mode not in self.DB_MODES:
                raise ValueError(
                    f"invalid mode {mode!r}, need one of {self.DB_MODES!r}"
                )
            dbname += f"?mode={mode}"

        self._read_only = mode in ("ro",)

        # print(dbname)
        self._conn = sqlite3.connect(
            dbname,
            uri=True,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )

        if not self._has_table("CURSBNR") and not self._read_only:
            self._create_main_table()

        if not self._has_table("CURSBNR_NO_VALUE") and not self._read_only:
            self._create_no_value_table()

    def _has_table(self, tablename: str):
        return (
            self._exec_fetchone(
                "SELECT COUNT(*)\nFROM sqlite_schema\nWHERE name == ?",
                (tablename,),
            )[0]
            > 0
        )

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    @property
    def in_transaction(self):
        return self._conn.in_transaction

    def begin(self):
        self._exec("BEGIN")

    def close(self):
        self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def get_currencies(self) -> list[str]:
        return self._exec_fetch_column("SELECT currency FROM CURSBNR GROUP BY currency", value=str)

    def get_date_range(self, currency=None) -> tuple[Date | None, Date | None]:

        sql, params = self._sql_where(
            "SELECT MIN(date), MAX(date) FROM CURSBNR", currency=currency
        )

        mind, maxd = self._exec_fetchone(sql, params)
        return to_date_opt(mind), to_date_opt(maxd)

    def put_value(
        self,
        date: _DateT,
        currency: str,
        value: _NumT | None,
    ) -> None:
        if not self.in_transaction:
            self.begin()

        if value is not None:
            self.insert_value(date, currency, value, replace=True)
            self.unset_no_value(date, currency)
        else:
            self.set_no_value(date, currency)
            self.remove_rows(date, currency)

    def put_rows(self, rows: Iterable[_OptValueRowT]) -> None:
        value_rows: list[_ValueRowT] = []
        no_value_rows: list[_NoValueRowT] = []

        for date, currency, value in rows:
            if value is not None:
                value_rows.append((date, currency, value))
            else:
                no_value_rows.append((date, currency))

        if not self.in_transaction:
            self.begin()

        self.insert_many_values(value_rows, replace=True)
        self.unset_many_no_values(value_rows)
        self.set_many_no_values(no_value_rows)
        self.delete_many_values(no_value_rows)

    def insert_many_values(
        self, rows: Iterable[_ValueRowT], *, replace: bool | None = None
    ) -> None:
        value_rows = (
            (to_date(date), require_str(currency), to_numeric(value))
            for date, currency, value in rows
        )
        return self._exec_many(
            "INSERT"
            + self._sql_or_action(replace=replace)
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            value_rows,
        )

    def delete_many_values(self, rows: Iterable[_OptOrNoValueRowT]) -> None:
        no_value_rows = (
            (to_date(date), require_str(currency)) for date, currency, *_ in rows
        )
        return self._exec_many(
            "DELETE FROM CURSBNR WHERE date = ? AND currency = ?", no_value_rows
        )

    def unset_many_no_values(self, rows: Iterable[_OptOrNoValueRowT]) -> None:
        no_value_rows = (
            (to_date(date), require_str(currency)) for date, currency, *_ in rows
        )
        return self._exec_many(
            "DELETE FROM CURSBNR_NO_VALUE WHERE date = ? AND currency = ?",
            no_value_rows,
        )

    def set_many_no_values(self, rows: Iterable[_OptOrNoValueRowT]):
        no_value_rows = (
            (to_date(date), require_str(currency)) for date, currency, *_ in rows
        )
        return self._exec_many(
            "INSERT OR IGNORE INTO CURSBNR_NO_VALUE (date, currency) VALUES (?, ?)",
            no_value_rows,
        )

    def insert_value(
        self,
        date: _DateT,
        currency: str,
        value: _NumT,
        *,
        replace: bool | None = None,
    ):
        date = to_date(date)
        require_str(currency)
        value = to_numeric(value)
        self._exec(
            "INSERT "
            + self._sql_or_action(replace=replace)
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date, currency, value),
        )

    def get_value(self, date: _DateT, currency: str) -> Numeric | None:
        date = to_date(date)
        require_str(currency)
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
        sql, params = self._sql_where(
            "DELETE FROM CURSBNR", date=date, currency=currency
        )

        self._exec(sql, params)

    def remove_many_rows(self, dates_currencies: Iterable[tuple[_DateT, str]]):
        sql = "DELETE FROM CURSBNR WHERE date = ? AND currency = ?"
        param_rows = (
            (to_date(date), require_str(currency))
            for date, currency in dates_currencies
        )
        self._exec_many(sql, param_rows)

    def select_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> list[ValueRow]:

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
        return self._exec_fetchall_rows(sql, params, type=ValueRow)

    def has_no_value(self, date: _DateT, currency: str) -> bool:
        date = to_date(date)
        require_str(currency)
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
        require_str(currency)

        self._exec(
            "INSERT OR IGNORE INTO CURSBNR_NO_VALUE (date, currency) VALUES (?, ?)",
            (date, currency),
        )

    def unset_no_value(
        self,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
    ):
        sql, params = self._sql_where(
            "DELETE FROM CURSBNR_NO_VALUE", date=date, currency=currency
        )

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

        return self._exec_fetchall_rows(sql, params, type=NoValueRow)

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

    def _exec_fetchall_rows(
        self,
        sql: str,
        params: list = [],
        *,
        type: Type[_NamedTuple_T],
    ) -> list[_T]:
        cursor = self._conn.execute(sql, params)
        try:
            return list(starmap(type, cursor))
        finally:
            cursor.close()

    def _exec_fetchall_apply(
        self,
        sql: str,
        params: list = [],
        *,
        func: Callable[[Any], _T],
    ) -> list[_T]:
        cursor = self._conn.execute(sql, params)
        try:
            return list(map(func, cursor))
        finally:
            cursor.close()

    def _exec_fetch_column(
        self,
        sql: str,
        params: list = [],
        *,
        value: Type[_T] | Callable[[Any], _T] = lambda value: value,
        column: int | str = 0,
    ) -> list[_T]:

        return self._exec_fetchall_apply(sql, params, func=lambda row: value(row[column]))

    def _exec(self, sql: str, params: list = []) -> None:
        self._conn.execute(sql, params).close()

    def _exec_fetchone(self, sql: str, params: list = []) -> Any:
        cursor = self._conn.execute(sql, params)
        try:
            return cursor.fetchone()
        finally:
            cursor.close()

    def _exec_many(self, sql: str, param_rows: Iterable[list]) -> None:
        self._conn.executemany(sql, param_rows).close()

    @staticmethod
    def _sql_or_action(*, replace: bool | None = None):
        return {None: "", True: " OR REPLACE", False: " OR IGNORE"}[replace]

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
            sql += sep + "currency in (" + ", ".join(["?"] * len(currency)) + ")"
            params.extend(map(require_str, currency))
            sep = _AND_

        else:
            require_str(currency)
            sql += sep + "currency = ?"
            params.append(currency)
            sep = _AND_

        return sql, params
