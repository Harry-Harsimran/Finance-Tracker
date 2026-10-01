import calendar
from datetime import date, datetime

MONTH_FMT = "%Y-%m"


def this_month():
    return date.today().strftime(MONTH_FMT)


def shift_month(m, delta):
    y, mo = map(int, m.split("-"))
    idx = y * 12 + (mo - 1) + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def month_label(m):
    y, mo = map(int, m.split("-"))
    return f"{calendar.month_name[mo]} {y}"


def money(v):
    return f"Rs {v:,.2f}"


def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def today_str():
    return date.today().isoformat()
