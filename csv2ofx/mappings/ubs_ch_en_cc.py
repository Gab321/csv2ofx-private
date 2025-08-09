# -*- coding: iso-8859-1 -*-
# vim: sw=4:ts=4:expandtab
"""
csv2ofx.mappings.ubs-ch-en-cc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping for a UBS credit card CSV with columns:
Account number, Card number, Account/Cardholder, Purchase date,
Booking text, Sector, Amount, Original currency, Rate, Currency,
Debit, Credit, Booked

We do two things:
1) Filter out any row lacking a valid Purchase date (blank, etc.).
2) Stop reading at row -3 (skip the last three lines, which are always summary/blank).
"""

import datetime
from operator import itemgetter

def parse_amount(row):
    """
    Convert Debit => negative, Credit => positive.
    Example: if 'Debit' is '453.68', that becomes -453.68.
             if 'Credit' is '12.34', that becomes +12.34.
    """
    debit_str = row["Debit"].strip()
    credit_str = row["Credit"].strip()
    if debit_str:
        return -float(debit_str.replace(",", "."))
    elif credit_str:
        return float(credit_str.replace(",", "."))
    return 0.0

def parse_payee(row):
    """Set 'Booking text' as Payee."""
    return row.get("Booking text", "").strip()

def parse_desc(row):
    """
    Combine 'Sector' and 'Booking text' for the memo field.
    """
    sector = row.get("Sector", "").strip()
    booking = row.get("Booking text", "").strip()

    combined = []
    if sector:
        combined.append(f"Sector: {sector}")
    if booking:
        combined.append(booking)

    return " / ".join(combined)

def skip_rows_with_blank_date(row):
    """
    Return False if Purchase date is missing or not parseable; True otherwise.
    """
    raw_date = row.get("Purchase date", "").strip()
    if not raw_date:
        # If there's no Purchase date, skip the row
        return False

    # Make sure it can parse as dd.mm.yyyy
    try:
        datetime.datetime.strptime(raw_date, "%d.%m.%Y")
    except ValueError:
        return False

    return True

mapping = {
    "has_header": True,
    "delimiter": ";",            # The file is semicolon-separated.

    # Start at the first row after the header, and stop 3 lines from the end
    # so we avoid the blank line plus the two summary lines.
    "first_row": 0,
    "last_row": -2,

    # This indicates how to parse the date:
    "date": itemgetter("Purchase date"),
    "parse_fmt": "%d.%m.%Y",

    # Hard-code currency as CHF (or read from row["Currency"] if desired)
    "currency": lambda row: "CHF",

    # Turn Debit/Credit columns into a single numeric field
    "amount": parse_amount,

    # Use 'Booking text' as Payee
    "payee": parse_payee,

    # Use 'Sector' + 'Booking text' as Memo
    "desc": parse_desc,

    # Skip rows if there's no valid Purchase date
    "filter": skip_rows_with_blank_date,
}

