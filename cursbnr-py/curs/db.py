import datetime as dt
import re
import sqlite3
from datetime import date as _date
from datetime import datetime
from datetime import time as _time
from functools import partial
from itertools import starmap
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, NamedTuple, Type, TypeVar

from textwrap import dedent

from curs.types import (
    Date,
    Numeric,
    DateCurrencyRow,
    DateCurrencyValueRow,
    DateCurrencyOptValueRow,
    _DateT,
    _NumT,
    require_str,
    to_date,
    to_date_opt,
    to_numeric,
    to_numeric_opt,
)

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

        if not self._read_only:
            if not self._has_table("CURSBNR"):
                self._create_main_table()

            self._make_value_null()

            if self._has_table("CURSBNR_NO_VALUE"):
                self._merge_no_value_table()

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
        return self._exec_fetch_column(
            "SELECT currency FROM CURSBNR GROUP BY currency", value=str
        )

    def get_date_range(self, currency=None) -> tuple[Date | None, Date | None]:

        sql, params = self._sql_where(
            "SELECT MIN(date), MAX(date) FROM CURSBNR",
            currency=currency,
            value_is_null=False,
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

        self.insert_value(date, currency, value, replace=True)

    def put_rows(self, rows: Iterable[_OptValueRowT]) -> None:
        self.insert_many_values(rows, replace=True)

    def insert_many_values(
        self, rows: Iterable[_OptValueRowT], *, replace: bool | None = None
    ) -> None:
        value_rows = (
            (to_date(date), require_str(currency), to_numeric_opt(value))
            for date, currency, value in rows
        )
        return self._exec_many(
            "INSERT"
            + self._sql_or_action(replace=replace)
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            value_rows,
        )

    def delete_many_values(
        self, rows: Iterable[_OptOrNoValueRowT], *, are_you_sure: bool
    ) -> None:
        if not are_you_sure:  # <(°.°)>
            return

        no_value_rows = (
            (to_date(date), require_str(currency)) for date, currency, *_ in rows
        )
        return self._exec_many(
            "DELETE FROM CURSBNR WHERE date = ? AND currency = ?", no_value_rows
        )

    def insert_value(
        self,
        date: _DateT,
        currency: str,
        value: _NumT | None,
        *,
        replace: bool | None = None,
    ):
        date = to_date(date)
        require_str(currency)
        value = to_numeric_opt(value)
        self._exec(
            "INSERT "
            + self._sql_or_action(replace=replace)
            + " INTO CURSBNR (date, currency, value) VALUES (?, ?, ?)",
            (date, currency, value),
        )

    def value(self, date: _DateT, currency: str) -> Numeric | None:
        date = to_date(date)
        require_str(currency)
        result = self._exec_fetchone(
            """
            SELECT value FROM CURSBNR WHERE date <= ? AND currency == ?
            ORDER BY date DESC
            LIMIT 1
            """,
            [date, currency],
        )
        if result is not None:
            return result[0]

    def get_value(self, date: _DateT, currency: str) -> DateCurrencyValueRow | None:
        date = to_date(date)
        require_str(currency)
        result = self._exec_fetchone(
            """
            SELECT date, currency, value FROM CURSBNR WHERE date<=? AND currency=? 
            ORDER BY date DESC
            """,
            [date, currency],
        )
        if result is not None:
            return DateCurrencyValueRow(*result)

    def remove_rows(
        self,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        *,
        value_is_null: bool = None,
        are_you_sure: bool,
    ):
        if not are_you_sure:  # <(°.°)>
            return

        sql, params = self._sql_where(
            "DELETE FROM CURSBNR",
            date=date,
            currency=currency,
            value_is_null=value_is_null,
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
        value_is_null: bool,  # = None
    ) -> list[DateCurrencyOptValueRow] | list[DateCurrencyValueRow]:

        sql, params = self._sql_where(
            "SELECT date, currency, value FROM CURSBNR",
            date=date,
            currency=currency,
            value_is_null=value_is_null,
        )

        sql += self._sql_order_by(orderby)

        row_type = (
            DateCurrencyValueRow if value_is_null == False else DateCurrencyOptValueRow
        )

        return self._exec_fetchall_rows(sql, params, type=row_type)

    def select_value_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
    ) -> list[DateCurrencyValueRow]:

        sql, params = self._sql_where(
            "SELECT date, currency, value FROM CURSBNR",
            date=date,
            currency=currency,
            value_is_null=False,
        )

        sql += self._sql_order_by(orderby)

        return self._exec_fetchall_rows(sql, params, type=DateCurrencyValueRow)

    @property
    def total_changes(self) -> int:
        return self._exec_fetchone("SELECT total_changes();")[0]

    def select_date_currency_rows(
        self,
        *,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
        orderby: str | None = None,
        value_is_null: bool = None,
    ) -> list[tuple[Date, str]]:
        sql, params = self._sql_where(
            "SELECT date, currency FROM CURSBNR",
            date=date,
            currency=currency,
            value_is_null=value_is_null,
        )

        return self._exec_fetchall_rows(sql, params, type=DateCurrencyRow)

    # ---------

    def _has_table(self, tablename: str):
        return (
            self._exec_fetchone(
                "SELECT COUNT(*)\nFROM sqlite_schema\nWHERE name == ?",
                (tablename,),
            )[0]
            > 0
        )

    def _create_main_table(self):
        self._exec(
            """
            CREATE TABLE CURSBNR(
                date DATE NOT NULL,
                currency TEXT NOT NULL,
                value NUMERIC NULL,
                PRIMARY KEY (date, currency)
            ) WITHOUT ROWID
            """
        )

    def _make_value_null(self):
        sql = self._exec_fetchone(
            "SELECT sql FROM sqlite_schema WHERE name == ?",
            ("CURSBNR",),
        )[0]

        if re.match(r"(?sxi) .* value \s+ NUMERIC \s+ NOT \s+ NULL \s* ,", sql):
            self._exec("ALTER TABLE CURSBNR RENAME TO _CURSBNR_VALUE")
            self._create_main_table()
            self._exec(
                """
                INSERT INTO CURSBNR (date, currency, value)
                SELECT date, currency, value FROM _CURSBNR_VALUE
                """
            )
            self._exec("DROP TABLE _CURSBNR_VALUE")

    def _merge_no_value_table(self):
        self._exec(
            """
            INSERT INTO CURSBNR (date, currency)
            SELECT date, currency FROM CURSBNR_NO_VALUE
            """
        )
        self._exec("DROP TABLE CURSBNR_NO_VALUE")

    # ---------

    def _exec_fetchall_rows(
        self,
        sql: str,
        params: list = [],
        *,
        type: Type[_NamedTuple_T],
    ) -> list[_T]:
        cursor = self._conn.execute(dedent(sql), params)
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
        cursor = self._conn.execute(dedent(sql), params)
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

        return self._exec_fetchall_apply(
            sql, params, func=lambda row: value(row[column])
        )

    def _exec(self, sql: str, params: list = []) -> None:
        self._conn.execute(dedent(sql), params).close()

    def _exec_fetchone(self, sql: str, params: list = []) -> Any:
        cursor = self._conn.execute(dedent(sql), params)
        try:
            return cursor.fetchone()
        finally:
            cursor.close()

    def _exec_many(self, sql: str, param_rows: Iterable[list]) -> None:
        self._conn.executemany(dedent(sql), param_rows).close()

    @staticmethod
    def _sql_or_action(*, replace: bool | None = None):
        return {None: "", True: " OR REPLACE", False: " OR IGNORE"}[replace]

    @staticmethod
    def _sql_where(
        sql: str,
        params: list = [],
        *,
        value_is_null: bool | None,
        date: _DateT | tuple[_DateT, _DateT] | None = None,
        currency: str | list[str] | None = None,
    ) -> tuple[str, list]:
        params = list(params)
        sep = "\nWHERE "
        _AND_ = " AND "

        if value_is_null is not None:
            sql += (
                sep + "value" + {False: " IS NOT NULL", True: " IS NULL"}[value_is_null]
            )
            sep = _AND_

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

    @staticmethod
    def _sql_order_by(orderby: None | str | list[str]):
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
            return "\nORDER BY\n    " + ",".join(orderby)
        else:
            return ""
