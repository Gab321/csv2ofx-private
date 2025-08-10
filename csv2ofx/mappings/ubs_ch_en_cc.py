# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
csv2ofx.mappings.ubs_ch_en_cc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robust mapping for UBS credit-card CSV (English), tolerant to:
- header wording changes (2024 vs 2025),
- ; delimiter,
- ISO-8859-1 or UTF-8 encodings,
- decimal comma and thousands separators,
- weird text like "DO&amp;CO" (amounts still parsed),
- optional summary/footer lines (drop with CLI -R -2).
"""

import re
from datetime import datetime

# --- helpers ---------------------------------------------------------------

def _normkeys(row):
    # case-insensitive, strip spaces and BOM if any
    return { (k or "").replace("\ufeff","").strip().lower(): v for k, v in row.items() }

def getv(row, *candidates):
    m = _normkeys(row)
    for name in candidates:
        key = (name or "").strip().lower()
        if key in m and m[key] is not None:
            return str(m[key])
    return ""

def _to_num(s):
    s = (s or "").strip()
    if not s:
        return 0.0
    s = s.replace("\xa0", " ").replace("'", "")  # nbsp + thousands
    s = s.replace(",", ".")                       # decimal comma -> dot
    s = re.sub(r"[^\d.\-]", "", s)               # strip CHF, spaces, etc.
    return float(s) if s else 0.0

def parse_date_iso(row):
    """
    Accepts multiple column names and formats and returns an ISO string.
    2024 exports: 'Purchase date' as dd.mm.yyyy
    2025 exports sometimes tweak wording/case.
    """
    raw = getv(row, "Purchase date", "Transaction date", "Date", "Booking date", "Booked date")
    raw = raw.strip()
    # Try common formats
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    # If none matched, leave empty (row will be filtered out)
    return ""

def parse_amount(row):
    # Prefer Debit (negative), else Credit (positive), else Amount
    debit  = getv(row, "Debit", "Debit amount")
    credit = getv(row, "Credit", "Credit amount")
    val = _to_num(debit)
    if val:
        return -val
    val = _to_num(credit)
    if val:
        return val
    return _to_num(getv(row, "Amount"))

def parse_payee(row):
    # Booking text / Description / Merchant
    return (getv(row, "Booking text", "Description", "Merchant") or "").strip()

def parse_desc(row):
    # Sector / MCC / Category + booking text
    sector  = (getv(row, "Sector", "MCC", "Category") or "").strip()
    booking = (getv(row, "Booking text", "Description", "Merchant") or "").strip()
    parts = []
    if sector:
        parts.append(f"Sector: {sector}")
    if booking:
        parts.append(booking)
    return " / ".join(parts)

def keep_row(row):
    # keep row only if a date exists & can be normalized
    return bool(parse_date_iso(row))

# --- mapping ---------------------------------------------------------------

mapping = {
    "has_header": True,
    "delimiter": ";",
    "first_row": 1,        # <-- skip the 'sep=;' line automatically
    # DO NOT set 'last_row' here; pass -R -2 on older exports when needed.

    "date": parse_date_iso,
    "parse_fmt": "%Y-%m-%d",

    "currency": lambda r: (getv(r, "Currency") or "CHF").strip(),
    "amount": parse_amount,
    "payee": parse_payee,
    "desc": parse_desc,

    "filter": keep_row,
}