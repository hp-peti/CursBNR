#!/usr/bin/env python3

# %%
from collections.abc import Iterable
import re
import threading
import time
from argparse import ArgumentParser, Namespace
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from sys import argv
from typing import Final

from curs.client import CursClient, Date

# %%
from curs.db import CursDB
from curs.threadutils import thread_local_cached
from curs.types import DateCurrencyOptValueRow, to_date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from suds import WebFault
from tqdm import tqdm


def main():
    args = parse_args()

    def get_db_file_name(__file__, args):
        if args.db is None:
            db_file = Path(__file__).parent / "bnr.db"
        else:
            db_file = Path(args.db)
            if not db_file.parent.exists() or not db_file.parent.is_dir():
                raise AssertionError(f"invalid db file path {db_file!s}")
        return db_file

    # import logging
    # logging.basicConfig(level='DEBUG')

    commit_every_n = 1024

    autoexclude: Final[bool] = True

    # %%

    db = CursDB(get_db_file_name(__file__, args))

    # %%

    thread_lock = threading.Lock()

    @thread_local_cached
    def get_client() -> CursClient:
        return CursClient(use_local_wsdl=not True)

    # %%

    client = get_client()

    _before_first_valid_date: dict[str, Date] = invert_date_to_curr_list(
        before_first_valid_date_
    )

    _last_valid_date: dict[str, Date] = invert_date_to_curr_list(last_valid_date_)

    # %%
    currencies, all_currencies = get_currencies(
        _before_first_valid_date, _last_valid_date, client
    )
    print(" ".join(all_currencies))

    xcache = set()

    for date, currency in db.select_date_currency_rows(
        currency=all_currencies, value_is_null=None
    ):
        xcache.add((date, currency))

    tpx = ThreadPoolExecutor(len(currencies) + len(_last_valid_date))

    # %%

    start_date, end_date = get_start_date_end_date(args, client)

    days = list(
        map(
            lambda d: d.date(),
            rrule(DAILY, start_date, until=end_date),
        )
    )
    days.reverse()
    loop = tqdm(days, leave=False)

    prev_total_changes = db.total_changes
    try:
        inserted = 0

        def after_insert(count: int):
            nonlocal inserted, commit_every_n, loop, db
            inserted += count
            if inserted >= commit_every_n:
                loop.set_postfix_str("COMMITING...  ")
                db.commit()
                inserted = 0

        def fetch(date, currency) -> DateCurrencyOptValueRow | None:
            try:
                loop.set_postfix_str(f"{date} {currency}")
                r_date, r_currency, r_value = get_client().get_value(date, currency)
                if r_date != date:
                    return DateCurrencyOptValueRow(date, currency, None)
                else:
                    return DateCurrencyOptValueRow(r_date, r_currency, r_value)
            except WebFault as wf:
                with thread_lock:
                    tqdm.write(f"{wf!s} @{date} {currency})")
                    if autoexclude:
                        if re.fullmatch(
                            r".*Object reference not set to an instance of an object\..*",
                            str(wf),
                        ):
                            tqdm.write(f"Skipping {currency} before {date}")
                            exclude_currency.append(currency)

        exclude_currency = []
        for date in loop:
            futures: list[Future] = []

            try:
                for currency, a_date in list(_last_valid_date.items()):
                    if date <= _last_valid_date[currency]:
                        if currency not in currencies:
                            currencies.append(currency)
                        del _last_valid_date[currency]

                for currency in currencies:
                    if (date, currency) in xcache:
                        # xcache.remove((date, currency))
                        continue  # inner loop

                    if currency in _before_first_valid_date:
                        if date <= _before_first_valid_date[currency]:
                            exclude_currency.append(currency)
                            del _before_first_valid_date[currency]

                            continue  # inner loop

                    if not db.select_rows(
                        date=date, currency=currency, value_is_null=None
                    ):
                        futures.append(tpx.submit(fetch, date, currency))
                        time.sleep(0.001)

            finally:

                def get_result(f: Future):
                    return f.result()

                def is_not_None(r) -> bool:
                    return r is not None

                results = list(filter(is_not_None, map(get_result, futures)))
                futures.clear()
                db.put_rows(results)
                after_insert(len(results))

            if exclude_currency:
                for currency in exclude_currency:
                    currencies.remove(currency)
                exclude_currency.clear()

                if not currencies:
                    break  # outer loop

    except KeyboardInterrupt:
        pass

    finally:
        print(f"{db.total_changes - prev_total_changes} rows affected.")
        db.commit()


def invert_date_to_curr_list(
    dates_to_currencies: Iterable[tuple[str, str | tuple[str, ...] | list[str]]],
) -> dict[str, Date]:
    return {
        curr_str: to_date(date)
        for date, curr_str_or_sequence in dates_to_currencies
        for curr_str in (
            curr_str_or_sequence
            if isinstance(curr_str_or_sequence, list | tuple)
            else (curr_str_or_sequence,)
        )
    }


def get_currencies(
    before_first_valid_date: dict[str, Date],
    last_valid_date: dict[str, Date],
    client: CursClient,
):
    if True:
        currencies = list(map(lambda x: x[0], client.get_all()))
    else:
        currencies = list(before_first_valid_date.keys())

    all_currencies = sorted(list(set(currencies + list(last_valid_date.keys()))))
    return currencies, all_currencies


def parse_args():
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "--db", metavar="DB", type=str, help="target database", default=None
    )

    start_date_args = arg_parser.add_mutually_exclusive_group()

    start_date_args.add_argument(
        "--start-date",
        metavar="YYYY-MM-DD",
        type=to_date,
        help="earliest date to retrieve",
        default=None,
    )
    arg_parser.add_argument(
        "--end-date",
        metavar="YYYY-MM-DD",
        type=to_date,
        help="latest date to retrieve",
        default=None,
    )

    start_date_args.add_argument(
        "--days",
        metavar="DAYS",
        type=int,
        help="days to go back",
        default=None,
    )

    start_date_args.add_argument(
        "--months",
        metavar="DAYS",
        type=int,
        help="months to go back",
        default=None,
    )

    start_date_args.add_argument(
        "--years",
        metavar="DAYS",
        type=int,
        help="years to go back",
        default=None,
    )
    del start_date_args

    args = arg_parser.parse_args(argv[1:])
    return args


def get_start_date_end_date(args: Namespace, client: CursClient) -> tuple[Date, Date]:
    start_date = to_date("1998-01-01")
    if args.start_date is not None:
        start_date = to_date(args.start_date)
    end_date = (
        client.lastdate
        if args.end_date is None
        else min(client.lastdate, to_date(args.end_date))
    )

    if args.days is not None:
        start_date = to_date(end_date - relativedelta(days=args.days - 1))
    if args.months is not None:
        start_date = to_date(end_date - relativedelta(months=args.months, days=-1))
    if args.years is not None:
        start_date = to_date(end_date - relativedelta(years=args.years, days=-1))

    return start_date, end_date


before_first_valid_date_: list[tuple[str, str | tuple[str, ...] | list[str]]] = [
    ("2017-06-18", "THB"),
    (
        "2009-03-01",
        (
            "AED",
            "BRL",
            "CNY",
            "INR",
            "KRW",
            "MXN",
            "NZD",
            "RSD",
            "UAH",
            "ZAR",
        ),
    ),
    ("2007-12-02", "BGN"),
    ("2007-11-11", "RUB"),
    ("2005-01-02", "TRY"),
    (
        "2001-11-11",
        (
            "CZK",
            "HUF",
            "PLN",
        ),
    ),
    ("1999-01-13", "EUR"),
    (
        "1998-01-04",
        (
            "AUD",
            "CAD",
            "CHF",
            "DKK",
            "EGP",
            "GBP",
            "JPY",
            "MDL",
            "NOK",
            "SEK",
            "USD",
            "XAU",
            "XDR",
        ),
    ),
    ("2015-08-20", "HRK"),
    (
        "2024-09-22",
        (
            "HKD",
            "IDR",
            "ILS",
            "ISK",
            "MYR",
            "PHP",
            "SGD",
        ),
    ),
]

last_valid_date_: list[tuple[str, str | tuple[str, ...] | list[str]]] = [
    ("2022-12-31", "HRK"),
]


if __name__ == "__main__":
    main()
