# Household Chores — Backlog (prioritized)

This backlog is a compact, prioritized list of work items to build the app in Django. Grouped by epic, with minimal acceptance criteria.

## 1 — Project setup (priority: High)
- Create Django project + `chores` app (migrations applyable).  
  Acceptance: `manage.py migrate` runs; admin accessible.
- Add basic settings, templates, `requirements.txt`.

## 2 — Core models & admin (priority: High)
- Implement `Member`, `Chore`, `Completion`, `Miss`, `Unlock`.  
  Acceptance: models migrate; admin shows and edits records.
- Add `Chore.advance()` behavior and `is_overdue` property.

## 3 — Scheduling service (priority: High)
- Implement `services/scheduling.py` with `next_due(...)`.  
  Acceptance: unit tests for daily/interval/weekly behavior pass.

## 4 — Chore CRUD, claim, complete (priority: High)
- Views/forms for create/edit/list.  
- Endpoints: `/chores/new/`, `/chores/<id>/edit/`, `/chores/<id>/claim/`, `/chores/<id>/complete/`.  
  Acceptance: completing a chore creates `Completion`, advances/archives chore.

## 5 — Members & session switching (priority: High)
- Members listing, create/edit, and `member_switch` view that sets `session['member_id']`.  
  Acceptance: session persists selected member; views show current member.

## 6 — Today view & misses recording (priority: High)
- Today page: Overdue / Due today / Upcoming grouping and nav counts.  
- Implement `record_misses()` to upsert `Miss` rows and roll recurring due dates forward.  
  Acceptance: missed claimed chores create `Miss`; overdue counts shown.

## 7 — Streaks & calendar (priority: Medium)
- `services/streaks.py`: `current_streak`, `longest_streak`, `calendar_30`.  
  Acceptance: functions return correct values for seeded data; components render 30-day dots.

## 8 — Achievements & levels (priority: Medium)
- `services/achievements.py`: badge rules, `xp_for`, `level_for`, `evaluate`.  
  Acceptance: `evaluate()` creates idempotent `Unlock` rows; trophies page lists unlocked items.

## 9 — UI/UX & HTMX interactions (priority: Medium)
- Add HTMX for claim/complete row swaps, unlock modal, and partial updates.  
  Acceptance: HTMX endpoints return partial templates and in-page updates without full reloads.

## 10 — Tests & fixtures (priority: Medium)
- Add `test_scheduling.py`, `test_streaks.py`, `test_achievements.py`.  
- Add a `demo` fixture with 3 members and ~8 chores.  
  Acceptance: tests run under `python manage.py test`; demo fixture loads with `loaddata`.

## 11 — Polish & extras (priority: Low)
- Tailwind styling, celebratory modal animation, export/import, optional cron reminders.  
  Acceptance: visual polish and optional management commands documented.

---

If you want, I can convert these into individual GitHub issues or wire up the first set of tests and fixtures next.
