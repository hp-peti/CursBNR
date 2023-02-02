# %%
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from tqdm import tqdm

# %%
from cursdb import CursDB
db = CursDB("bnr.db")

start_date = "2017-01-01"
commit_every_n = 1024

# %%
from cursclient import CursClient
from curstypes import to_date
client = CursClient()

# %%
currencies = list(map(lambda x: x[1], client.getall()))
print(*currencies, sep=", ")

# %%
days = list(rrule(DAILY, to_date(start_date), until=client.lastdate))
days.reverse()
loop = tqdm(days, leave=False)
try:
    inserted = 0
    for date in loop:
        for currency in currencies:
            if (value := db.get_value(date, currency)) is None:
                loop.set_postfix_str(f"{date.date()} {currency}")

                value = client.getvalue(date, currency)

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



