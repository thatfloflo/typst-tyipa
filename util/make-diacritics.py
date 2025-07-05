"""Script to auto-generate TyIPA diacritic functions."""
from pathlib import Path
from datetime import datetime
import csv

infile = Path.cwd() / "src" / "_diacritics.csv"
code_file = Path.cwd() / "src" / "_diacritics.typ"
manual_file = Path.cwd() / "manual" / "_list-diacritics.typ"


FUNC_HEADER = [
    '/// Apply the \'{ipa_desc}\' diacritic to `base`.',
    '/// ',
    '/// Adds the following diacritic to `base`:',
    '/// / IPA name: {ipa_name}',
    '/// / IPA description: {ipa_desc}',
    '/// / Unicode name: {unicode_name}',
    '/// / Unicode hex: `0x{unicode_hex}`',
    '/// / TyIPA name: {tyipa_name}',
    '/// / TyIPA alias(es): {tyipa_aliases}',
    '/// ',
    '/// -> str',
    '#let {tyipa_name}(',
    '  /// The character(s) to which the diacritic should be added.',
    '  /// -> str | symbol',
    '  base',
    ') = {{',
]


def gen_accent_func(d: dict[str, str]) -> str:
    """Generate code for a Typst accent/diacritic function based on `d`."""
    o = FUNC_HEADER.copy()
    if d["group"] == "segmentation" and d["tyipa-name"].startswith("tied-"):
        o.append('  assert(')
        o.append('    type(base) == str,')
        o.append('    message: "{tyipa_name}() expects argument of type `str`, `" + str(type(base)) + "` given"')
        o.append('  )')
        o.append('  let parts = base.split("")')
        o.append('  assert(')
        o.append('    parts.len() == 4,')
        o.append('    message: "{tyipa_name}() expects argument of length 2, " + str(parts.len() - 2) + " given"')
        o.append('  )')
        o.append('  parts.at(1) + "\\u{{{unicode_hex}}}" + parts.at(2)')
    else:
        o.append('  let modified = ()')
        o.append('  for chr in str(base) {{')
        o.append('    modified.push(chr + "\\u{{{unicode_hex}}}")')
        o.append('  }}')
        o.append('  modified.join("")')
    o.append('}}')
    o.append('\n')
    return "\n".join(o).format(
        group=d["group"],
        ipa_name=d["ipa-name"],
        ipa_desc=d["ipa-desc"],
        unicode_name=d["unicode-name"],
        unicode_hex=d["unicode-hex"],
        tyipa_name=d["tyipa-name"],
        tyipa_aliases=d["tyipa-aliases"] or "(none)",
    )


def gen_alias(orig: str, alias: str) -> str:
    """Generate code for aliasing a function in Typst."""
    o = []
    o.append('/// Alias for `{orig}`.')
    o.append('#let {alias} = {orig}')
    o.append('\n')
    return "\n".join(o).format(
        orig=orig,
        alias=alias
    )


def gen_section_head(group: str) -> str:
    """Generate a comment for section headin in Typst."""
    return f"/*** {group.capitalize()} diacritics***/\n\n"


def gen_manual_section_head(group: str) -> str:
    """Generate a Typst markup heading for a section in the manual."""
    return f"\n== {group.title()}\n\n"


def gen_manual_display_code(d: dict[str, str]) -> str:
    """Generate Typst display code for a diacritic function in the manual."""
    symbol = ""
    aliases = ""
    notes = ""
    type_sig = "str | symbol"
    code = f'{d["tyipa-name"]}(base: {type_sig})'
    if d["group"] == "segmentation" and d["tyipa-name"].startswith("tied-"):
        type_sig = "str"
        symbol = f'ipa.diac.{d["tyipa-name"]}(ipa.sym.placeholder + ipa.sym.placeholder)'
        code = f'{d["tyipa-name"]}(base: {type_sig})'
        notes = '  note: "Expects an argument of length exactly 2.",\n'
    else:
        symbol = f'ipa.diac.{d["tyipa-name"]}(ipa.sym.placeholder)'
    if d["tyipa-aliases"]:
        aliases = f'  aliases: ("{d["tyipa-aliases"]}(base: {type_sig})",),\n'
    return (
        '#display-diac(\n'
        f'  {symbol},\n'
        f'  "{code}",\n'
        f'  "{d["ipa-name"]}",\n'
        f'  "{d["ipa-desc"]}",\n'
        f'  escape: "\\\\u{{{d["unicode-hex"]}}}",\n'
        f'{aliases}{notes}'
        ')\n'
    )


print("Reading diacritics from:", infile)

with infile.open("r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    diacritics = [row for row in reader]

print(f"Done. {len(diacritics)} diacritic definitions found.")


print("Writing accent functions to:", code_file)

with code_file.open("w+", encoding="utf-8") as f:
    f.write("/// Accenting functions for the diacritics of the IPA.\n")
    f.write("/// \n")
    f.write("/// This file was auto-generated. Re-run the package's\n")
    f.write("/// `./util/make-diacritics.py` script if you have\n")
    f.write("/// updated the definitions in `./src/_diacritics.csv`.\n")
    f.write("/// \n")
    f.write("/// File generated on: ")
    f.write(datetime.now().replace(microsecond=0).isoformat())
    f.write(f"\n/// Definitions included: {len(diacritics)}\n")
    f.write("\n")
    last_section = ""
    for diacritic in diacritics:
        if diacritic["group"] != last_section:
            last_section = diacritic["group"]
            f.write(gen_section_head(last_section))
        f.write(gen_accent_func(diacritic))
        if diacritic["tyipa-aliases"]:
            for alias in diacritic["tyipa-aliases"].split(" "):
                print("Name:", diacritic["tyipa-name"])
                f.write(gen_alias(diacritic["tyipa-name"], alias))

print("Done.")

print("Writing diacritic display list to:", manual_file)

with manual_file.open("w+", encoding="utf-8") as f:
    f.write("/// Display listing of tyipa diacritic functions.\n")
    f.write("/// \n")
    f.write("/// This file was auto-generated. Re-run the package's\n")
    f.write("/// `./util/make-diacritics.py` script if you have\n")
    f.write("/// updated the definitions in `./src/_diacritics.csv`.\n")
    f.write("/// \n")
    f.write("/// File generated on: ")
    f.write(datetime.now().replace(microsecond=0).isoformat())
    f.write(f"\n/// Definitions included: {len(diacritics)}\n")
    f.write("\n")
    f.write('#import "../src/lib.typ" as ipa\n')
    f.write('#import "./_display-layouts.typ": display-diac\n')
    f.write("\n")
    last_section = ""
    for diacritic in diacritics:
        if diacritic["group"] != last_section:
            last_section = diacritic["group"]
            f.write(gen_manual_section_head(last_section))
        f.write(gen_manual_display_code(diacritic))


print("All done.")
