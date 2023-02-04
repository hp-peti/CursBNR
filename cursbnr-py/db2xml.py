from cursxml import write_bnr_xml
from cursdb import CursDB
from curstypes import CursMap

# %%
db = CursDB("bnr.db")

map = CursMap()
for date, currency, value in db.select_rows():
    map.put_value(date, currency, value)


write_bnr_xml(map, "bnr.xml")

print(f"Written {map.get_size()} items.")