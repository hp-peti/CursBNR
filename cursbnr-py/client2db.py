# %%
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm
from suds import WebFault

# %%
from cursdb import CursDB
from curstypes import to_date

db = CursDB("bnr.db")

start_date = "2014-01-01"
commit_every_n = 1024
exclude_currency_before = {"THB": to_date("2017-06-19")}

# %%
from cursclient import CursClient

client = CursClient()

# %%
currencies = list(map(lambda x: x[1], client.getall()))
print(*currencies, sep=", ")

# %%
days = list(rrule(DAILY, to_date(start_date), until=client.lastdate))
days.reverse()
loop = tqdm(days, leave=False)
excluded_currency = set()
try:
    inserted = 0
    for date in loop:
        for currency in currencies:
            if currency in excluded_currency:
                continue
            else:
                if currency in exclude_currency_before:
                    if exclude_currency_before[currency] >= date.date():
                        excluded_currency.add(currency)
                        del exclude_currency_before[currency]

            if (value := db.get_value(date, currency)) is None:
                loop.set_postfix_str(f"{date.date()} {currency}")

                try:
                    value = client.getvalue(date, currency)
                except WebFault as wf:
                    tqdm.write(f"{wf!s} @{date.date()} {currency})")

                if value is not None:
                    db.insert_value(date, currency, value, replace=False)
                    inserted += 1
                    if inserted >= commit_every_n:
                        loop.set_postfix_str("COMMITING...  ")
                        db.commit()
                        inserted = 0

except KeyboardInterrupt:
    pass
finally:
    db.commit()


# %%
