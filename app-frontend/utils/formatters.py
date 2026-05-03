from datetime import datetime


def format_number(n, precision=0):
    try:
        if precision == 0:
            return f"{int(n):,}"
        return f"{n:,.{precision}f}"
    except Exception:
        return str(n)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    if dt is None:
        return ""
    try:
        return dt.strftime(fmt)
    except Exception:
        return str(dt)
