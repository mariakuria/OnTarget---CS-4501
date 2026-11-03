## User story

As a job candidate, I want tasks written for my specific company's interview style, so that my prep matches what I will actually be asked.

## Acceptance criteria

- [ ] The planner sends the LLM the company name, the number of days and the list of problem ids, and calls it once when the first answer is usable.
- [ ] A valid JSON answer becomes the plan, and the plan's source is "llm".
- [ ] JSON wrapped in code fences or surrounded by extra text is still read.
- [ ] A coding task whose problem_id is in the catalog keeps the link. An unknown problem_id is dropped and the plan still succeeds.
- [ ] The Anthropic client reads ANTHROPIC_API_KEY and fails with a clear error if it is missing.

## Tests

Written first (TDD) in `tests/test_llm_plan.py`. Commit the failing tests, then the code that makes them pass.
