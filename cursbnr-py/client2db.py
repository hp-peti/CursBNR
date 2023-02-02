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


start_date = "1990-01-01"
commit_every_n = 1024
before_first_valid_date = {
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
    "TRY": to_date('2005-01-02'),
    "CZK": to_date('2001-11-11'),
    "HUF": to_date('2001-11-11'),
    "PLN": to_date('2001-11-11'),
    # "---": to_date('2009-XX-XX'),
    # "---": to_date('2009-XX-XX'),
    # "---": to_date('2009-XX-XX'),
    "THB": to_date("2017-06-18"),
}
autoexclude = True

# %%

db = CursDB("bnr.db")
client = CursClient()

# %%
currencies = list(map(lambda x: x[1], client.getall()))
print(*currencies, sep=", ")

xcache = set()
for date, currency, _ in db.select_rows(currency=currencies):
    xcache.add((date, currency))

# %%
days = list(
    map(lambda d: d.date(), rrule(DAILY, to_date(start_date), until=client.lastdate))
)
days.reverse()
loop = tqdm(days, leave=False)
exclude_currency = []
try:
    inserted = 0
    for date in loop:
        for currency in currencies:
            if (date, currency) in xcache:
                xcache.remove((date, currency))
                continue

            if currency in before_first_valid_date:
                if date <= before_first_valid_date[currency]:
                    exclude_currency.append(currency)
                    del before_first_valid_date[currency]

                    continue  # inner loop

            if (value := db.get_value(date, currency)) is None:
                loop.set_postfix_str(f"{date} {currency}")

                try:
                    value = client.getvalue(date, currency)
                except WebFault as wf:
                    tqdm.write(f"{wf!s} @{date} {currency})")
                    if autoexclude:
                        if re.fullmatch(
                            r".*Object reference not set to an instance of an object\..*",
                            str(wf),
                        ):
                            tqdm.write(f"Skipping {currency} before {date}")
                            exclude_currency.append(currency)

                if value is not None:
                    db.insert_value(date, currency, value, replace=False)
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
                break # outer loop


except KeyboardInterrupt:
    pass
finally:
    db.commit()


# %%
