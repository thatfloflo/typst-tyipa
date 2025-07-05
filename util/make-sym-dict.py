"""Script to auto-generate a dictionary of known TyIPA symbols."""
from pathlib import Path
from datetime import datetime
import re

infile = Path.cwd() / "src" / "sym.typ"
outfile = Path.cwd() / "src" / "_sym-dict.typ"

print("Reading from:", infile)

sym_def_pattern = r"^[\t ]*#let[\t ]+([a-zA-Z\-]+)[\t ]*=[\t ]*symbol\([\t ]*(?://.*)*$"
sym_primary_pattern = r"^[\t ]*\"(\S)\"[\t ]*,[\t ]*(?://.*)*$"
sym_secondary_pattern = r"^[\t ]*\([\t ]*\"([a-zA-Z\-\.]+)\"[\t ]*,[\t ]*\"(\S)\"\)[\t ]*,[\t ]*(?://.*)*"

symbols = dict()

with infile.open("r", encoding="utf8") as f:
    currentsym = None
    for line in f.readlines():
        match = re.match(sym_def_pattern, line)
        if match:
            currentsym = match.groups()[0]
            continue
        match = re.match(sym_primary_pattern, line)
        if match:
            symbols[currentsym] = match.groups()[0]
            continue
        match = re.match(sym_secondary_pattern, line)
        if match:
            symbols[f"{currentsym}.{match.groups()[0]}"] = match.groups()[1]

print(f"Done. {len(symbols)} symbol definitions found.")

print("Writing to:", outfile)

with outfile.open("w+", encoding="utf8") as f:
    f.write("/// Internal dictionary of known symbols.\n")
    f.write("/// \n")
    f.write("/// This file was generated automatically by a script.\n")
    f.write("/// Re-run the package's ./util/make-sym-dict.py script\n")
    f.write("/// if you have updated the definitions in ./src/sym.typ.\n")
    f.write("/// \n")
    f.write("/// File generated on: ")
    f.write(datetime.now().replace(microsecond=0).isoformat())
    f.write(f"\n/// Symbol definitions included: {len(symbols)}\n")
    f.write("\n")
    f.write("#let sym-dict = (\n")
    for key, value in symbols.items():
        f.write(f'  "{key}": "{value}",\n')
    f.write(")\n")
