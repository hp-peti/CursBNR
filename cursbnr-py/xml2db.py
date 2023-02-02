# %%
from curstypes import CursMap
from cursxml import parse_bnr_xml
from cursdb import CursDB

# %%
db = CursDB("bnr.db")


# %%
map = parse_bnr_xml("bnr.xml")


# %%

inserted = 0
for date, currency, value in map.rows():
    db.insert_value(date, currency, value, replace=False)

db.commit()

