# %%
from pathlib import Path
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm
from suds import WebFault
import re
import time
from concurrent.futures import Future, ThreadPoolExecutor
from threading import local as threading_local

# %%
from curs.db import CursDB
from curs.client import CursClient
from curs.types import CursMap, to_date

#import logging
#logging.basicConfig(level='DEBUG')

start_date = "1998-01-01"
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
    "HRK": to_date("2015-08-20")
}

last_valid_date = {
    "HRK": to_date("2022-12-31"),
}

autoexclude = True

# %%

db = CursDB(Path(__file__).parent / "bnr.db")

# %%

thread_local = threading_local()
def get_client(use_local_wsdl: bool = False) -> CursClient:
    global thread_local
    if not hasattr(thread_local,"client"):
        thread_local.client = CursClient(use_local_wsdl=use_local_wsdl)
    return thread_local.client

# %%

client = get_client()

# %%
if 0:
    currencies = list(map(lambda x: x[0], client.get_all()))
else:
    currencies = list(last_valid_date.keys())

all_currencies = sorted(list(set(currencies + list(last_valid_date.keys()))))
print(" ".join(all_currencies))

xcache = set()
for date, currency, _ in db.select_rows(currency=all_currencies):
    xcache.add((date, currency))

for date, currency in db.select_no_value_rows(currency=all_currencies):
    xcache.add((date, currency))

tpx = ThreadPoolExecutor(len(currencies) + len(last_valid_date))


# %%
days = list(
    map(lambda d: d.date(), rrule(DAILY, to_date(start_date), until=client.lastdate))
)
days.reverse()
loop = tqdm(days, leave=False)
try:
    inserted = 0
    def after_insert():
        global inserted, commit_every_n, loop, db
        inserted += 1
        if inserted >= commit_every_n:
            loop.set_postfix_str("COMMITING...  ")
            db.commit()
            inserted = 0

    def fetch(date, currency):
        try:
            loop.set_postfix_str(f"{date} {currency}")

            r_date, r_currency, r_value = get_client().get_value(date, currency)
        except WebFault as wf:
            tqdm.write(f"{wf!s} @{date} {currency})")
            if autoexclude:
                if re.fullmatch(
                    r".*Object reference not set to an instance of an object\..*",
                    str(wf),
                ):
                    tqdm.write(f"Skipping {currency} before {date}")
                    exclude_currency.append(currency)

        if r_date != date:
            return lambda db: db.set_no_value(date, currency)

        else:
            return lambda db: db.insert_value(r_date, r_currency, r_value, replace=False)


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
                    xcache.remove((date, currency))
                    continue # inner loop

                if currency in before_first_valid_date:
                    if date <= before_first_valid_date[currency]:
                        exclude_currency.append(currency)
                        del before_first_valid_date[currency]

                        continue  # inner loop

                if (db_value := db.get_value(date, currency)) is None:
                    futures.append(tpx.submit(fetch, date, currency))
                    time.sleep(0)

        finally:
            for future in futures:
                future.result()(db)
                after_insert()

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
