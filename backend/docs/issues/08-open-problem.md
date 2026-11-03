## User story

As a job candidate, I want to open a coding task and see the full problem with starter code in my language, so that I can practice inside the app.

## Acceptance criteria

- [ ] GET /problems lists the seven catalog problems with id, title and difficulty.
- [ ] GET /problems/{id} returns title, difficulty, topics, description, examples and constraints.
- [ ] Every problem has starter code for Python, Java, C++ and JavaScript.
- [ ] An unknown problem id returns 404.
- [ ] Every problem_id used by a coding task in a new plan exists in the catalog.

## Tests

Written first (TDD) in `tests/test_problems.py`. Commit the failing tests, then the code that makes them pass.
