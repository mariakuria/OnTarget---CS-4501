## User story

As a busy job candidate, I want to skip a day I cannot study, so that one missed day does not make my plan look failed.

## Acceptance criteria

- [ ] PATCH /plans/{id}/days/{day_number} with {"skipped": true} marks the day skipped. Day numbers start at 1.
- [ ] Tasks in skipped days are left out of both done and total.
- [ ] Setting skipped to false brings the tasks back into progress.
- [ ] Skipping every day gives total 0 and percent 0, with no error.
- [ ] An unknown plan or day number returns 404.
- [ ] The change is saved.

## Tests

Written first (TDD) in `tests/test_skip_day.py`. Commit the failing tests, then the code that makes them pass.
