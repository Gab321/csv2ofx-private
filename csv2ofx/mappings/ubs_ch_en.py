# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
csv2ofx.mappings.ubs-ch-en
~~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping for UBS Switzerland (English).
"""

import locale
from operator import itemgetter

# If needed, set an English locale or skip if not required
# locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

def parse_amount(row):
    """Combine Debit and Credit into a single numeric amount."""
    debit_str = row["Debit"].strip()
    credit_str = row["Credit"].strip()
    if debit_str:
        return float(debit_str.replace(",", "."))
    elif credit_str:
        return float(credit_str.replace(",", "."))
    return 0.0

def parse_payee(row):
    """Pick whichever column is your real 'Payee'.
       If Description1 is typically the payee, parse that.
    """
    return row["Description1"].strip() or row["Description2"].strip()

def parse_desc(row):
    """Put everything else in the main description (memo) field."""
    d2 = row["Description2"].strip()
    d3 = row["Description3"].strip()
    foot = row["Footnotes"].strip()
    # Combine them with slashes or line breaks:
    combined = []
    if d2:
        combined.append(d2)
    if d3:
        combined.append(d3)
    if foot:
        combined.append(foot)
    return " / ".join(combined)

mapping = {
    "has_header": True,
    "delimiter": ";",

    "date": itemgetter("Value date"),
    "parse_fmt": "%Y-%m-%d",
    "currency": itemgetter("Currency"),
    "amount": parse_amount,

    # This will become <NAME> in the OFX
    "payee": parse_payee,

    # This will become <MEMO> in the OFX
    "desc": parse_desc,

    # If you want a separate <NOTE>, you can define:
    # "notes": lambda r: r["Footnotes"] or ""
}

