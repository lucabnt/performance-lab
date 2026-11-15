"""Spreadsheet formula neutralization for exported CSV text cells (RT-15).

A text cell starting with = + - @ tab or CR is prefixed with an apostrophe, so a
spreadsheet shows it as text instead of evaluating it. Numbers, including text
that already reads as a number (``-12.5``, ``-12,5``), are left untouched.
Fuorigiri imports remove the apostrophe again: the mapping is reversible, also
for text that originally started with an apostrophe.
"""
import csv

PREFIXES = ('=', '+', '-', '@', '\t', '\r')


def _numeric(text):
    try:
        float(text.replace(',', '.'))
        return True
    except ValueError:
        return False


def _needs_prefix(text):
    if not text:
        return False
    if text[0] in PREFIXES:
        return not _numeric(text)
    return text[0] == "'" and _needs_prefix(text[1:])


def neutralize(value):
    return "'" + value if isinstance(value, str) and _needs_prefix(value) else value


def restore(value):
    if isinstance(value, str) and value.startswith("'") and _needs_prefix(value[1:]):
        return value[1:]
    return value


class DictWriter(csv.DictWriter):
    def writerow(self, rowdict):
        return super().writerow({k: neutralize(v) for k, v in rowdict.items()})

    def writerows(self, rowdicts):
        return super().writerows({k: neutralize(v) for k, v in row.items()} for row in rowdicts)


class writer:
    def __init__(self, stream, **options):
        self._writer = csv.writer(stream, **options)

    def writerow(self, row):
        return self._writer.writerow([neutralize(v) for v in row])

    def writerows(self, rows):
        return self._writer.writerows([neutralize(v) for v in row] for row in rows)
