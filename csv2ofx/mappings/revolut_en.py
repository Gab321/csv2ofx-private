# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
csv2ofx.mappings.revolut
~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping for Revolut CSV transactions.

- Extracts Payee from 'Description'
- Formats Memo/Notes with 'Type' and 'Description'
- Filters out 'REVERTED' transactions
"""

from operator import itemgetter

def parse_amount(row):
    """
    Extracts the transaction amount.
    - Negative values represent expenses (debits).
    - Positive values represent income (credits).
    """
    amount_str = row["Amount"].strip()
    if not amount_str:
        return 0.0  # Fallback to zero if missing
    return float(amount_str.replace(",", "."))

def parse_payee(row):
    """
    Extracts the Payee from the 'Description' field.
    - Example: 'Google Play' -> Payee: 'Google Play'
    - Example: 'Top-Up by *1701' -> Payee: 'Revolut Top-Up'
    """
    desc = row["Description"].strip()
    
    # Normalize Top-Ups and Payments
    if "Top-Up" in desc:
        return "Revolut Top-Up"
    elif "Payment from Gabriel Wehrli" in desc:
        return "Revolut Transfer"
    
    return desc  # Default to description if no specific handling needed

def parse_desc(row):
    """
    Combines 'Type' and 'Description' into the transaction memo.
    - Example: 'CARD_PAYMENT' + 'Google Play' -> "CARD_PAYMENT / Google Play"
    """
    type_ = row["Type"].strip()
    desc = row["Description"].strip()
    return f"{type_} / {desc}"

def skip_reverted(row):
    """
    Filters out transactions with 'REVERTED' state.
    """
    state = row.get("State", "").strip().upper()
    return state != "REVERTED"  # Only keep non-reverted transactions

mapping = {
    "has_header": True,
    "delimiter": ",",  # Revolut CSV is comma-separated

    "date": itemgetter("Started Date"),
    "parse_fmt": "%Y-%m-%d %H:%M:%S",  # Adjusted for datetime parsing

    "currency": itemgetter("Currency"),
    "amount": parse_amount,

    "payee": parse_payee,  # Now correctly extracting Payee
    "desc": parse_desc,  # Memo includes Type and Description

    "filter": skip_reverted,  # Skip REVERTED transactions
}

