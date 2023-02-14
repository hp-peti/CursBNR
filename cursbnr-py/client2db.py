#!/usr/bin/env python3

# %%
from pathlib import Path
from typing import Tuple
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm
from suds import WebFault
import re
import time
from concurrent.futures import Future, ThreadPoolExecutor
import threading

# %%
from curs.db import CursDB
from curs.client import CursClient
from curs.types import CursMap, to_date, Date, Numeric, DateCurrencyOptValueRow

from pathlib import Path

from argparse import ArgumentParser
from sys import argv

arg_parser = ArgumentParser()

arg_parser.add_argument(
    "--db", metavar="DB", type=str, help="target database", default=None
)
arg_parser.add_argument(
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
args = arg_parser.parse_args(argv[1:])

if args.db is None:
    db_file = Path(__file__).parent / "bnr.db"
else:
    db_file = Path(args.db)
    if not db_file.parent.exists() or not db_file.parent.is_dir():
        raise AssertionError(f"invalid db file path {db_file!s}")


# import logging
# logging.basicConfig(level='DEBUG')

start_date = "1998-01-01"
if args.start_date is not None:
    start_date = args.start_date
if args.end_date is not None:
    end_date = args.end_date

commit_every_n = 1024
before_first_valid_date = {
    "THB": to_date("2017-06-18"),
    "AED": to_date("2009-03-01"),
    "BRL": to_date("2009-03-01"),
    "CNY": to_date("2009-03-01"),
    "INR": to_date("2009-03-01"),
    "KRW": to_date("2009-03-01"),
    "MXN": to_date("2009-03-01"),
    "NZD": to_date("2009-03-01"),
    "RSD": to_date("2009-03-01"),
    "UAH": to_date("2009-03-01"),
    "ZAR": to_date("2009-03-01"),
    "BGN": to_date("2007-12-02"),
    "RUB": to_date("2007-11-11"),
    "TRY": to_date("2005-01-02"),
    "CZK": to_date("2001-11-11"),
    "HUF": to_date("2001-11-11"),
    "PLN": to_date("2001-11-11"),
    "EUR": to_date("1999-01-13"),
    "AUD": to_date("1998-01-04"),
    "CAD": to_date("1998-01-04"),
    "CHF": to_date("1998-01-04"),
    "DKK": to_date("1998-01-04"),
    "EGP": to_date("1998-01-04"),
    "GBP": to_date("1998-01-04"),
    "JPY": to_date("1998-01-04"),
    "MDL": to_date("1998-01-04"),
    "NOK": to_date("1998-01-04"),
    "SEK": to_date("1998-01-04"),
    "USD": to_date("1998-01-04"),
    "XAU": to_date("1998-01-04"),
    "XDR": to_date("1998-01-04"),
    "HRK": to_date("2015-08-20"),
}

last_valid_date = {
    "HRK": to_date("2022-12-31"),
}

autoexclude = True

# %%

db = CursDB(db_file)

# %%

thread_local = threading.local()
thread_lock = threading.Lock()


def get_client() -> CursClient:
    global thread_local
    if not hasattr(thread_local, "client"):
        thread_local.client = CursClient(use_local_wsdl=not True)
    return thread_local.client


# %%

client = get_client()

# %%
if True:
    currencies = list(map(lambda x: x[0], client.get_all()))
else:
    currencies = list(before_first_valid_date.keys())

all_currencies = sorted(list(set(currencies + list(last_valid_date.keys()))))
print(" ".join(all_currencies))

xcache = set()

for date, currency in db.select_date_currency_rows(
    currency=all_currencies, value_is_null=None
):
    xcache.add((date, currency))

tpx = ThreadPoolExecutor(len(currencies) + len(last_valid_date))


# %%

end_date=client.lastdate if args.end_date is None else min(client.lastdate, to_date(args.end_date))

days = list(
    map(
        lambda d: d.date(),
        rrule(DAILY, to_date(start_date), until=end_date),
    )
)
days.reverse()
loop = tqdm(days, leave=False)

try:
    inserted = 0

    def after_insert(count: int):
        global inserted, commit_every_n, loop, db
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
            for currency, a_date in list(last_valid_date.items()):
                if date <= last_valid_date[currency]:
                    if currency not in currencies:
                        currencies.append(currency)
                    del last_valid_date[currency]

            for currency in currencies:
                if (date, currency) in xcache:
                    # xcache.remove((date, currency))
                    continue  # inner loop

                if currency in before_first_valid_date:
                    if date <= before_first_valid_date[currency]:
                        exclude_currency.append(currency)
                        del before_first_valid_date[currency]

                        continue  # inner loop

                if not db.select_rows(date=date, currency=currency, value_is_null=None):
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
    db.commit()


# %%
