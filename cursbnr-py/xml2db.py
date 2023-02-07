# %%
from curstypes import CursMap
from cursxml import parse_bnr_xml
from cursdb import CursDB


# %%
db = CursDB("bnr.db")

# %%
map = parse_bnr_xml("bnr.xml")

print(f"Read {map.get_size()} items.")

# %%

for date, currency, value in map.all_rows():
    db.put_value(date, currency, value)

db.commit()
