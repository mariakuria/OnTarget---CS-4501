## User story

As a job candidate, I want to enter a company and date in a web page and see, tick off and practice my plan there, so that I can use OnTarget without writing any API calls.

## Acceptance criteria

- [ ] Opening / in a browser shows the OnTarget page with a company field, a date field and a Build my plan button.
- [ ] The page uses the same server for plans and problems, with no hard-coded server address and no external scripts.
- [ ] The page shows whether the plan was written by the AI or is the standard fallback plan.
- [ ] Ticking a task or skipping a day updates the progress and is saved through the API.
- [ ] Opening a coding task shows the problem and an editor; code results are simulated in this version.
- [ ] The API routes and /docs still work, and an unknown path returns 404.

## Tests

Written first (TDD) in `tests/test_ui.py`. Commit the failing tests, then the code that makes them pass.
