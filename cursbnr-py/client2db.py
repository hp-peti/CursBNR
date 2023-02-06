# %%
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm
from suds import WebFault
import re

# %%
from cursdb import CursDB
from cursclient import CursClient
from curstypes import CursMap, to_date


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

db = CursDB("bnr.db")
client = CursClient()

# %%
currencies = list(map(lambda x: x[1], client.getall()))

xcache = set()
for date, currency, _ in db.select_rows(currency=currencies):
    xcache.add((date, currency))

# %%
days = list(
    map(lambda d: d.date(), rrule(DAILY, to_date(start_date), until=client.lastdate))
)
days.reverse()
loop = tqdm(days, leave=False)
try:
    inserted = 0
    exclude_currency = []
    for date in loop:
        for currency, a_date in list(last_valid_date.items()):
            if date <= last_valid_date[currency]:
                if currency not in currencies:
                    currencies.append(currency)
                del last_valid_date[currency]

        for currency in currencies:
            if (date, currency) in xcache:
                xcache.remove((date, currency))
                continue

            if currency in before_first_valid_date:
                if date <= before_first_valid_date[currency]:
                    exclude_currency.append(currency)
                    del before_first_valid_date[currency]

                continue  # inner loop

            if (db_value := db.get_value(date, currency)) is None:
                loop.set_postfix_str(f"{date} {currency}")

                try:
                    r_date, r_currency, r_value = client.getvalueadv(date, currency)
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
                    continue

                db.insert_value(r_date, r_currency, r_value, replace=False)
                inserted += 1
                if inserted >= commit_every_n:
                    loop.set_postfix_str("COMMITING...  ")
                    db.commit()
                    inserted = 0

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
