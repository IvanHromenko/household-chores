from datetime import date, timedelta
from typing import List
from ..models import Completion, Miss


def current_streak(member) -> int:
    today = date.today()
    completions = set(Completion.objects.filter(member=member).values_list('date', flat=True))
    misses = set(Miss.objects.filter(member=member).values_list('date', flat=True))
    streak = 0
    for i in range(0, 400):
        d = today - timedelta(days=i)
        if d in misses:
            break
        if d in completions:
            streak += 1
        else:
            # neutral day
            continue
    return streak


def longest_streak(member) -> int:
    completions = set(Completion.objects.filter(member=member).values_list('date', flat=True))
    if not completions:
        return 0
    sorted_days = sorted(completions)
    longest = 0
    current = 1
    for a, b in zip(sorted_days, sorted_days[1:]):
        if (b - a).days == 1:
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    longest = max(longest, current)
    return longest


def calendar_30(member) -> List[dict]:
    today = date.today()
    completions = set(Completion.objects.filter(member=member).values_list('date', flat=True))
    misses = set(Miss.objects.filter(member=member).values_list('date', flat=True))
    out = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        state = 'idle'
        if d in completions:
            state = 'done'
        elif d in misses:
            state = 'miss'
        out.append({'date': d, 'state': state})
    return out
