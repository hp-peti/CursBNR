# %%
from curstypes import CursMap
from cursxml import parse_bnr_xml
from cursdb import CursDB

REMOVE_SUCCESSIVE_EQUAL_VALUES = False
REPLACE = False

# %%
db = CursDB("bnr.db")
if REMOVE_SUCCESSIVE_EQUAL_VALUES:
    db.remove_rows()

# %%
map = parse_bnr_xml("bnr.xml")

print(f"Read {map.get_size()} items.")

# %%

if REMOVE_SUCCESSIVE_EQUAL_VALUES:
    inserted = 0
    skipped = 0

    last_date_value = {}

    for date, currency, value in map.rows():
        last_date, last_value = last_date_value.get(currency, (None, None))
        assert last_date is None or last_date < date
        if last_value is not None and last_value != value:
            inserted += 1
            db.insert_value(date, currency, value)
        else:
            skipped += 1
        last_date_value[currency] = (date, value)
    db.commit()

    print(f"Inserted {inserted}, skipped {skipped} row(s).")

else:
    for date, currency, value in map.rows():
        if db.has_no_value(date, currency):
            continue
        db.insert_value(date, currency, value, replace=False)

    db.commit()
