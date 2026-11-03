## User story

As a job candidate with a technical interview coming up, I want to enter a company and my interview date and get a day-by-day prep plan, so that I know exactly what to do each day instead of studying at random.

## Acceptance criteria

- [ ] POST /plans with a company and a future interview date returns 201 with a plan id.
- [ ] The plan has one day per day until the interview, capped at 14 days. The last day is the day before the interview.
- [ ] Every day has at least one task, and every task starts as not done.
- [ ] Task ids are unique within a plan.
- [ ] The company name is trimmed.
- [ ] A missing, blank, or over-80-character company returns 422.
- [ ] A missing or invalid date, or a date that is today or earlier, returns 422.

## Tests

Written first (TDD) in `tests/test_create_plan.py`. Commit the failing tests, then the code that makes them pass.
