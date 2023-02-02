# %%
from cursxml import parse_bnr_xml
from cursdb import CursDB
from curstypes import CursMap

# %%
db = CursDB("bnr.xml.db")


# %%
map = parse_bnr_xml("bnr.xml")


# %%

for date, currency, value in map.rows():
    db.insert_value(date, currency, value, replace=False)

db.commit()


