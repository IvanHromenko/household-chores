# Household Chores — Streaks, Badges & Levels (Django Blueprint)

A single-device household chore tracker: local member profiles, self-claimed chores (recurring + one-off), streak tracking, and badges/levels that unlock at milestones (7, 30, 90-day streaks and more).

---

## 1. Product scope

**Members**
- Add/edit/remove member profiles on one shared device (name + emoji avatar + color).
- Tap a member to "become" them for the session — no login, no passwords.

**Chores**
- Create a chore: title, type (Recurring or One-off), frequency for recurring (daily / every N days / weekly on chosen weekdays), optional notes.
- Shared pool: any chore can be claimed by any member; claimed chores show the claimer.
- Complete a chore → logged with timestamp; recurring chores reschedule to the next due date, one-offs are archived.

**Reminders (in-app)**
- Today view: Overdue, Due today, Upcoming.
- Overdue items visually flagged with counts in the nav.
- No push/email in v1 (optional later via a management command + cron).

**Streaks**
- Per-member streak. Walking backwards from today: a day where the member missed a chore due to them breaks the streak; a day with completions extends it; a day with nothing due is neutral (streak preserved).
- Shows current streak, longest streak, and a 30-day dot calendar.

**Badges & Levels**
- Streak badges: 3-day Spark, 7-day Steady, 30-day Dedicated, 90-day Legend.
- Volume badges: 10 / 50 / 250 completions.
- Behavior badges: First Claim, No-Overdue Week, Full House Day.
- Levels 1–10 from XP: 10 XP per completion, +5 on time, +5 on a streak day.
- Unlock moment: celebratory modal on the next page render; trophy page shows unlocked badges in color, locked ones greyed with the requirement.

---

## 2. Tech stack

- Python 3.12, Django 5.x
- SQLite (single-device app — no Postgres needed)
- Django templates + HTMX for partial updates (no SPA build step)
- Tailwind via CDN or `django-tailwind` (optional)
- pytest-django for tests

```
pip install django htmx-django-middleware  # or just django
django-admin startproject config .
python manage.py startapp chores
```

---

## 3. Project layout

```text
household-chores/
  manage.py
  config/
    settings.py
    urls.py
  chores/
    models.py
    views.py
    urls.py
    forms.py
    services/
      scheduling.py      # next_due(), due-date math
      streaks.py         # streak computation
      achievements.py    # badge + level rules (pure functions)
    templates/chores/
      base.html
      today.html
      chore_list.html
      members.html
      trophies.html
      partials/_chore_row.html
      partials/_unlock_modal.html
    migrations/
    tests/
      test_scheduling.py
      test_streaks.py
      test_achievements.py
  _docs/plan.md
  requirements.txt
```

---

## 4. Data model (`chores/models.py`)

```python
class Member(models.Model):
    name = models.CharField(max_length=40)
    emoji = models.CharField(max_length=8, default="🧽")
    hue = models.IntegerField(default=20)          # 0-360, drives card color
    created_at = models.DateTimeField(auto_now_add=True)

class Chore(models.Model):
    RECURRING, ONEOFF = "recurring", "oneoff"
    DAILY, INTERVAL, WEEKLY = "daily", "interval", "weekly"

    title = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=[(RECURRING, "Recurring"), (ONEOFF, "One-off")])
    freq_kind = models.CharField(max_length=10, blank=True)   # daily|interval|weekly
    freq_interval = models.PositiveSmallIntegerField(default=1)
    freq_weekdays = models.JSONField(default=list)            # [0..6], Monday=0
    due_date = models.DateField()
    claimed_by = models.ForeignKey(Member, null=True, blank=True, on_delete=models.SET_NULL, related_name="claimed")
    archived = models.BooleanField(default=False)             # completed one-offs

    @property
    def is_overdue(self): ...
    def advance(self):    # set due_date = next_due(...)

class Completion(models.Model):
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    chore_title = models.CharField(max_length=120)   # denormalized, survives chore deletion
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="completions")
    date = models.DateField()
    on_time = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Miss(models.Model):
    """One row per (member, date) where a due claimed chore was not completed.
    Written lazily by the streak service so history stays stable."""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="misses")
    date = models.DateField()
    class Meta:
        unique_together = ("member", "date")

class Unlock(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="unlocks")
    kind = models.CharField(max_length=8)     # "badge" | "level"
    key = models.CharField(max_length=40)     # badge id, or level number as string
    date = models.DateField(auto_now_add=True)
    seen = models.BooleanField(default=False) # drives the celebration modal
    class Meta:
        unique_together = ("member", "kind", "key")
```

---

## 5. Services

### `services/scheduling.py`
```python
def next_due(from_date: date, freq_kind: str, interval: int, weekdays: list[int]) -> date
```
- `daily` → +1 day
- `interval` → +max(1, interval) days
- `weekly` → next date in the next 7 days whose weekday is in `weekdays`; fallback +7.

### `services/streaks.py`
```python
def current_streak(member) -> int
def longest_streak(member) -> int
def calendar_30(member) -> list[dict]   # {"date", "state": "done"|"miss"|"idle"}
```
Algorithm: collect `completion_dates` and `miss_dates` as sets. Walk back from today up to 400 days: `miss` → stop; `done` → `streak += 1`; otherwise skip. `longest_streak` runs the same scan across the whole history.

`record_misses()` is called on each page load: for every claimed, unarchived chore with `due_date < today`, upsert a `Miss` for `(claimed_by, due_date)` and, for recurring chores, roll `due_date` forward past the missed occurrences.

### `services/achievements.py` — pure, testable rules
```python
BADGES = [
    Badge("spark",     "Spark",             "3-day streak",       lambda s: s.streak >= 3),
    Badge("steady",    "Steady",            "7-day streak",       lambda s: s.streak >= 7),
    Badge("dedicated", "Dedicated",         "30-day streak",      lambda s: s.streak >= 30),
    Badge("legend",    "Legend",            "90-day streak",      lambda s: s.streak >= 90),
    Badge("ten",       "Getting Going",     "10 chores done",     lambda s: s.total >= 10),
    Badge("fifty",     "Workhorse",         "50 chores done",     lambda s: s.total >= 50),
    Badge("twofifty",  "Household Hero",    "250 chores done",    lambda s: s.total >= 250),
    Badge("first",     "First Claim",       "Claim your first chore", lambda s: s.claims >= 1),
    Badge("clean7",    "No-Overdue Week",   "7 days, nothing overdue", lambda s: s.clean_days >= 7),
    Badge("fullhouse", "Full House Day",    "Everyone finished on the same day", lambda s: s.full_house),
]

LEVELS = [(1,"Rookie",0),(2,"Helper",50),(3,"Tidy",120),(4,"Reliable",250),(5,"Committed",450),
          (6,"Champion",700),(7,"Machine",1000),(8,"Legendary",1400),(9,"Mythic",1900),(10,"Domestic God",2500)]

def xp_for(member) -> int          # 10/completion, +5 on_time, +5 if that day extended a streak
def level_for(xp) -> tuple[int, str, int, int]   # level, name, xp_into_level, xp_to_next
def evaluate(member) -> list[Unlock]             # create missing Unlock rows, return the new ones
```
`evaluate()` is idempotent (guarded by the `unique_together`) and is called after every completion and claim.

---

## 6. Views & URLs (`chores/urls.py`)

| Route | View | Purpose |
| --- | --- | --- |
| `/` | `today` | Member switcher, overdue/today/upcoming lists, streak + level bar |
| `/chores/` | `chore_list` | All chores, filters, create form |
| `/chores/new/` | `chore_create` | POST form |
| `/chores/<id>/edit/` | `chore_edit` | POST form |
| `/chores/<id>/claim/` | `chore_claim` | POST, HTMX swaps the row |
| `/chores/<id>/complete/` | `chore_complete` | POST → `Completion`, advance/archive, `evaluate()` |
| `/members/` | `member_list` | Manage profiles + per-member stats |
| `/members/switch/<id>/` | `member_switch` | Sets `request.session["member_id"]` |
| `/trophies/` | `trophies` | Badge grid, level ladder, 30-day streak calendar |

Active member lives in the Django session (`member_id`). A small context processor injects `current_member`, overdue count, and any unseen `Unlock` rows so `base.html` can render the celebration modal and then mark them `seen`.

---

## 7. Design

Warm, tactile "kitchen board" feel: paper-toned background, chunky rounded cards, bold flame accent for streaks, satisfying check animation on complete. Badge tiles are square medallions with a subtle inner glow when unlocked, flat grey with the requirement text when locked.

---

## 8. Build order

1. `startproject` / `startapp`, models + first migration, Django admin registration.
2. `scheduling.py` + tests.
3. Members page and session switching.
4. Chore CRUD, claim, complete (with `advance()` / archive).
5. Today view with overdue/today/upcoming grouping and `record_misses()`.
6. `streaks.py` + tests; streak bar and 30-day calendar.
7. `achievements.py` + tests; trophies page; unlock modal.
8. Seed fixture (`python manage.py loaddata demo`) with 3 members and ~8 chores.

---

## 9. Notes

- Everything is local to one SQLite file — no auth, so keep the app on a trusted device/LAN.
- Later upgrades: `django-q`/cron for real reminders, per-member PINs, Postgres + accounts for multi-device sync.
