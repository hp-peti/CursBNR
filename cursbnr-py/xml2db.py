# %%
from curs.types import CursMap
from curs.xml import parse_bnr_xml
from curs.db import CursDB

# %%
print("Opening database...")
db = CursDB("bnr.db")

# %%
print("Parsing XML...")
map = parse_bnr_xml("bnr.xml")

print(f"Read {map.get_size()} items.")

# %%

print("Updating database...")

db.put_rows(map.all_rows())

print("Committing...")
db.commit()
print("Done!")

# %%
