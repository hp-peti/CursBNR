#!/usr/bin/env python3

# %%
from pathlib import Path
from curs.xml import parse_bnr_xml
from curs.db import CursDB

from argparse import ArgumentParser
from sys import argv

arg_parser = ArgumentParser()

arg_parser.add_argument("--replace", action="store_true", default=False)
arg_parser.add_argument(
    "--xml", metavar="XML", type=str, help="source xml", default="bnr.xml"
)
arg_parser.add_argument(
    "--db", metavar="DB", type=str, help="target database", default=None
)

args = arg_parser.parse_args(argv[1:])
xml_file = Path(args.xml)
if not xml_file.exists() or not xml_file.is_file():
    raise AssertionError(f"invalid xml file path {xml_file!s}")

if args.db is None:
    db_file = Path(__file__).parent / "bnr.db"
else:
    db_file = Path(args.db)
    if not db_file.parent.exists() or not xml_file.parent.is_dir():
        raise AssertionError(f"invalid db file path {db_file!s}")

# %%
print("Opening database...")
db = CursDB(db_file)

# %%
print("Parsing XML...")
map = parse_bnr_xml(xml_file)

print(f"Read {map.get_size()} items.")

# %%

print("Updating database...")

prev_total_changes = db.total_changes
db.insert_many_values(map.all_rows(), replace=args.replace)
print(f"{db.total_changes - prev_total_changes} rows affected")
print("Committing...")
db.commit()
print("Done!")

# %%
