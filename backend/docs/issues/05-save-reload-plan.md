## User story

As a job candidate, I want my plan saved so I can come back to it, so that I do not lose my progress when I close the app.

## Acceptance criteria

- [ ] GET /plans/{id} returns the same plan that POST /plans returned.
- [ ] An unknown plan id returns 404.
- [ ] Plans are stored in SQLite and survive an app restart (a new app on the same database file).
- [ ] Each plan gets a different id.

## Tests

Written first (TDD) in `tests/test_persistence.py`. Commit the failing tests, then the code that makes them pass.
