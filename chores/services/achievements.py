from dataclasses import dataclass
from typing import Callable, List
from ..models import Unlock


@dataclass
class Badge:
    key: str
    name: str
    desc: str
    rule: Callable


BADGES = [
    Badge('spark', 'Spark', '3-day streak', lambda s: s.get('streak', 0) >= 3),
    Badge('steady', 'Steady', '7-day streak', lambda s: s.get('streak', 0) >= 7),
]


def xp_for(member) -> int:
    # simplified: 10 XP per completion
    from ..models import Completion
    return Completion.objects.filter(member=member).count() * 10


def level_for(xp):
    # simplified linear levels
    level = xp // 100 + 1
    return (level, f'Level {level}', xp % 100, 100 - (xp % 100))


def evaluate(member):
    # very small evaluator that creates Unlock rows when rules pass
    stats = {'streak': 0, 'total': 0}
    stats['total'] = member.completions.count()
    new = []
    for b in BADGES:
        if b.rule(stats):
            obj, created = Unlock.objects.get_or_create(member=member, kind='badge', key=b.key)
            if created:
                new.append(obj)
    return new
