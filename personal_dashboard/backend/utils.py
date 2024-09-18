import re
from datetime import datetime as dt
from datetime import timedelta


def get_last_week_dates():
    current_date = dt.now()
    start_of_current_week = current_date - timedelta(days=current_date.weekday())
    start_of_last_week = start_of_current_week - timedelta(weeks=1)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    formatted_dates = f"{start_of_last_week.day:02}-{end_of_last_week.day:02}"
    return formatted_dates


def get_day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "ᵗʰ"
    else:
        return ["ˢᵗ", "ⁿᵈ", "ʳᵈ"][day % 10 - 1]


def extract_first_date(date_string):
    if date_string is None:
        return "01"

    match = re.search(r"\b(\d+)", date_string)
    if match:
        number = int(match.group(1))
        return f"{number:02}"
