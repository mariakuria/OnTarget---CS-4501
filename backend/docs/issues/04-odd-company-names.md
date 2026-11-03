## User story

As a candidate interviewing at a small or lesser-known company, I want a full plan even if the AI has never heard of my company, so that the tool works for any employer, not just big tech.

## Acceptance criteria

- [ ] Names with letters from any language, digits, spaces and & . , ' + - ( ) ! / are accepted (AT&T, Nestlé, Procter & Gamble).
- [ ] Repeated spaces inside a name are collapsed to one.
- [ ] Names with line breaks or characters such as { } < > ` are rejected with 422, so they cannot inject instructions into the LLM prompt.
- [ ] The prompt tells the LLM to use general software interview prep when it does not know the company.
- [ ] A company the LLM knows nothing about still gets a full plan.

## Tests

Written first (TDD) in `tests/test_company_names.py`. Commit the failing tests, then the code that makes them pass.
