#!/usr/bin/env python3

from pathlib import Path
from curs.xml import write_bnr_xml
from curs.db import CursDB
from curs.types import CursMap

from argparse import ArgumentParser
from sys import argv

arg_parser = ArgumentParser()

arg_parser.add_argument("--xml", metavar="XML", type=str, help="target xml", default="bnr.xml")
arg_parser.add_argument("--db", metavar="DB", type=str, help="source database", default=None)

args = arg_parser.parse_args(argv[1:])
xml_file = Path(args.xml)
if not xml_file.parent.exists() or not xml_file.parent.is_dir():
    raise AssertionError(f"invalid xml file path {xml_file!s}")

if args.db is None:
    db_file = Path(__file__).parent / "bnr.db"
else:
    db_file = Path(args.db)

# %%
print("Opening database...")
db = CursDB(db_file, mode="ro")

print("Retrieving items...")
map = CursMap()
for date, currency, value in db.select_rows(value_is_null=None):
    map.put_value(date, currency, value)

print(f"Retrieved {map.get_size()} items.\nWriting XML file...")

write_bnr_xml(map, xml_file)

print(f"Done!")