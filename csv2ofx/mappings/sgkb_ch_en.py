# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
csv2ofx.mappings.sgkb-ch-en
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple SGKB Mapping: 
- Uses `Booking text` for both Payee and Memo.
- Works seamlessly with Actual Budget's rule matching.
"""

import datetime

def _normalize_header_keys(row):
    """Normalize column headers (lowercase, remove BOM if present)."""
    return {k.lower().strip().lstrip('\ufeff'): (v if v is not None else "").strip() for k, v in row.items()}

def _get_value(row, key):
    """Retrieve a column value from a row with normalized headers."""
    return _normalize_header_keys(row).get(key.lower().strip(), "")

def parse_amount(row):
    """Convert Debit/Credit into a single numeric amount."""
    debit = _get_value(row, "Debit").replace("'", "").replace(",", ".")
    credit = _get_value(row, "Credit").replace("'", "").replace(",", ".")

    if debit:
        return -float(debit) if debit.replace(".", "").isdigit() else 0.0
    elif credit:
        return float(credit) if credit.replace(".", "").isdigit() else 0.0
    return 0.0

def parse_booking_text(row):
    """Use `Booking text` for both Payee and Memo."""
    return _get_value(row, "Booking text")

def filter_valid_date(row):
    """Filter rows with invalid 'Booking date'."""
    raw_date = _get_value(row, "Booking date")
    try:
        datetime.datetime.strptime(raw_date, "%d.%m.%Y")
        return True
    except ValueError:
        print(f"⚠️ Skipping row with invalid date: {raw_date}")
        return False

mapping = {
    "has_header": True,
    "delimiter": ";",  # SGKB uses semicolon

    "date": lambda row: _get_value(row, "Booking date"),
    "parse_fmt": "%d.%m.%Y",

    "currency": lambda row: "CHF",
    "amount": parse_amount,

    # Both Payee and Memo = Booking Text
    "payee": parse_booking_text,
    "desc": parse_booking_text,

    "filter": filter_valid_date,
}

