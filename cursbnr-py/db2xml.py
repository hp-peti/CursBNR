#!/usr/bin/env python3

from pathlib import Path
from curs.xml import write_bnr_xml
from curs.db import CursDB
from curs.types import CursMap


# %%
print("Opening database...")
db = CursDB(Path(__file__).parent / "bnr.db", mode="ro")

print("Retrieving items...")
map = CursMap()
for date, currency, value in db.select_rows():
    map.put_value(date, currency, value)

for date, currency, in db.select_no_value_rows():
    map.put_value(date, currency, None)

print(f"Retrieved {map.get_size()} items.\nWriting XML file...")

write_bnr_xml(map, "bnr.xml")

print(f"Done!")