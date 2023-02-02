# %%
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm
from suds import WebFault
import re
# %%
from cursdb import CursDB
from curstypes import to_date

db = CursDB("bnr.db")

start_date = "2000-01-01"
commit_every_n = 1024
before_first_valid_date = {
    "THB": to_date("2017-06-18")
}
autoexclude = True

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
exclude_currency = []
try:
    inserted = 0
    for date in loop:
        for currency in currencies:
            if currency in before_first_valid_date:
                if date.date() <= before_first_valid_date[currency]:
                    exclude_currency.append(currency)
                    del before_first_valid_date[currency]
                    
                    continue # inner loop

            if (value := db.get_value(date, currency)) is None:
                loop.set_postfix_str(f"{date.date()} {currency}")

                try:
                    value = client.getvalue(date, currency)
                except WebFault as wf:
                    tqdm.write(f"{wf!s} @{date.date()} {currency})")
                    if autoexclude:
                        if re.fullmatch(r".*Object reference not set to an instance of an object\..*", str(wf)):
                            tqdm.write(f"Skipping {currency} before {date.date()}")
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


except KeyboardInterrupt:
    pass
finally:
    db.commit()


# %%
