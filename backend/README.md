# OnTarget backend (Alpha)

Enter a company and an interview date, get a day-by-day interview prep plan. An LLM writes the company-specific tasks. If it fails, a built-in default plan is used.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...            # optional; without it the default plan is used
uvicorn app.server:build_app --factory   # then open http://127.0.0.1:8000/docs
```

| Endpoint | What it does |
|---|---|
| `POST /plans` `{company, interview_date}` | Build and save a plan |
| `GET /plans/{id}` | Load a saved plan (includes `progress`) |
| `PATCH /plans/{id}/tasks/{task_id}` `{done}` | Check a task off |
| `PATCH /plans/{id}/days/{n}` `{skipped}` | Skip or unskip a day |
| `GET /problems`, `GET /problems/{id}` | Problem catalog with starter code |

Settings: `ONTARGET_DB` (default `ontarget.db`), plus one LLM option:

- Any OpenAI-compatible provider (Gemini, Groq, OpenRouter, Ollama): `ONTARGET_LLM_BASE_URL`, `ONTARGET_LLM_MODEL`, and `ONTARGET_LLM_API_KEY` (not needed for Ollama).
- Anthropic: `ANTHROPIC_API_KEY`, optionally `ONTARGET_MODEL` (default `claude-sonnet-5-5`).

If `ONTARGET_LLM_BASE_URL` is set it wins. With no LLM settings, the default plan is used.

## Tests and metrics

```bash
python3 -m pytest              # all tests; none call a real LLM
python3 scripts/metrics.py     # numbers for the slide, also written to docs/metrics.md
```

Every test carries `@pytest.mark.issue(n)` and starts as `ai_generated`. Put `@pytest.mark.manual` on any test you write or change yourself and the AI-vs-manual ratio updates.

## How the TDD history was made

For each issue `scripts/tdd.sh red N <file> "msg"` ran the new tests (they had to fail) and committed them, then the code was written and `scripts/tdd.sh green N <file> "msg"` committed it with `Closes #N`. `docs/tdd_log.md` records every red and green run; `git log` shows the test commit before each feature commit.

## Put it on GitHub

```bash
gh auth login
scripts/setup_github.sh ontarget-backend
```

This creates the repo, labels, an `Alpha` milestone and issues #1 to #8 from `docs/issues/`, then pushes. The issues are created first so the `Closes #N` commits close them.

## End-to-end demo

`python3 scripts/demo.py` runs the whole flow (plan, open a problem, check off tasks, skip a day, reload, tricky inputs). Add `--simulate-llm-outage` to show the fallback, or `--base-url http://127.0.0.1:8000` to run it against a live server.

## Known limits

- The real Anthropic call is covered only with a stub in tests; try it once with a key before the demo.
- The default plan repeats a theme when the interview is more than 7 days away.
- Run and Submit for code are not part of the backend (the frontend mocks them).
