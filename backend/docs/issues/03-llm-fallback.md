## User story

As a job candidate, I want to still get a plan if the AI service is down or answers badly, so that I am never blocked before an interview.

## Acceptance criteria

- [ ] If the LLM raises an error (including a timeout), POST /plans still returns 201 with source "fallback".
- [ ] An empty answer, text that is not JSON, the wrong number of days, a day with no tasks, an unknown task type, or a task with blank text all trigger the fallback.
- [ ] The fallback plan has the right number of days and mentions the company.
- [ ] A failed or unusable answer is retried, up to 3 attempts in total with a short wait between them, before the default plan is used.
- [ ] Every failed attempt is logged.

## Tests

Written first (TDD) in `tests/test_fallback.py`. Commit the failing tests, then the code that makes them pass.
