## User story

As a job candidate, I want to check off tasks and see how far along I am, so that I can tell if I am on track for the interview.

## Acceptance criteria

- [ ] Every plan response includes progress with done, total and percent.
- [ ] PATCH /plans/{id}/tasks/{task_id} with {"done": true} marks the task done and updates progress.
- [ ] Percent is round(100 * done / total), and 0 when total is 0.
- [ ] A task can be marked not done again.
- [ ] The change is saved.
- [ ] An unknown plan or task returns 404. A body without "done" returns 422.

## Tests

Written first (TDD) in `tests/test_progress.py`. Commit the failing tests, then the code that makes them pass.
