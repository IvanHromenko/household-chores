from datetime import date, timedelta
from typing import List


def next_due(from_date: date, freq_kind: str, interval: int, weekdays: List[int]) -> date:
    if freq_kind == 'daily':
        return from_date + timedelta(days=1)
    if freq_kind == 'interval':
        step = max(1, int(interval or 1))
        return from_date + timedelta(days=step)
    if freq_kind == 'weekly':
        # find next date in the next 7 days whose weekday is in weekdays
        if not weekdays:
            return from_date + timedelta(days=7)
        for i in range(1, 8):
            cand = from_date + timedelta(days=i)
            if cand.weekday() in weekdays:
                return cand
        return from_date + timedelta(days=7)
    # fallback: +1 day
    return from_date + timedelta(days=1)
