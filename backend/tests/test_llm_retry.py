"""Issue #3 (continued): retry the LLM a couple of times before using the default plan."""
import logging

import pytest

from tests.fakes import FlakyLLM, llm_plan_json

pytestmark = [pytest.mark.issue(3), pytest.mark.ai_generated]

GOOD = llm_plan_json(7)


def post(client):
    return client.post("/plans", json={"company": "Amazon", "interview_date": "2026-11-09"})


def test_a_bad_answer_is_retried_and_the_good_second_answer_is_used(make_client):
    llm = FlakyLLM(['{"days": [1, 2,,]}', GOOD])
    body = post(make_client(llm=llm)).json()
    assert body["source"] == "llm"
    assert len(llm.prompts) == 2


def test_an_error_is_retried(make_client):
    llm = FlakyLLM([TimeoutError("busy"), GOOD])
    assert post(make_client(llm=llm)).json()["source"] == "llm"
    assert len(llm.prompts) == 2


def test_the_third_attempt_can_still_succeed(make_client):
    llm = FlakyLLM([RuntimeError("503"), "not json", GOOD])
    assert post(make_client(llm=llm)).json()["source"] == "llm"
    assert len(llm.prompts) == 3


def test_it_gives_up_after_three_attempts_and_uses_the_default_plan(make_client):
    llm = FlakyLLM([RuntimeError("503")])
    body = post(make_client(llm=llm)).json()
    assert body["source"] == "fallback"
    assert len(llm.prompts) == 3


def test_a_successful_first_attempt_is_not_repeated(make_client):
    llm = FlakyLLM([GOOD])
    post(make_client(llm=llm))
    assert len(llm.prompts) == 1


def test_it_waits_between_attempts_but_not_after_the_last_one(make_client, monkeypatch):
    from app import planner

    waits = []
    monkeypatch.setattr(planner, "RETRY_DELAY_SECONDS", 0.25)
    monkeypatch.setattr(planner.time, "sleep", waits.append)
    post(make_client(llm=FlakyLLM([RuntimeError("503")])))
    assert waits == [0.25, 0.25]


def test_every_failed_attempt_is_logged(make_client, caplog):
    with caplog.at_level(logging.WARNING, logger="ontarget.planner"):
        post(make_client(llm=FlakyLLM([RuntimeError("first"), RuntimeError("second"), RuntimeError("third")])))
    text = " ".join(r.getMessage() for r in caplog.records)
    for word in ("first", "second", "third", "attempt 1/3", "attempt 3/3"):
        assert word in text
