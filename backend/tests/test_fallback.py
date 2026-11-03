"""Issue #3: fall back to a default plan when the LLM fails."""
import json
import logging

import pytest

from tests.fakes import FakeLLM, llm_plan_json

pytestmark = [pytest.mark.issue(3), pytest.mark.ai_generated]


def post(client, company="Amazon", interview_date="2026-11-09"):
    return client.post("/plans", json={"company": company, "interview_date": interview_date})


def with_days(days):
    return json.dumps({"days": days})


GOOD_TASK = {"type": "coding", "text": "Solve Two Sum", "problem_id": "two-sum"}


def seven(day):
    return with_days([day] * 7)


BAD_ANSWERS = {
    "empty answer": "",
    "plain text": "I'm sorry, I can't help with that.",
    "json array": "[1, 2, 3]",
    "missing days key": '{"plan": []}',
    "truncated json": llm_plan_json(7)[:-40],
    "too few days": llm_plan_json(5),
    "too many days": llm_plan_json(9),
    "day without tasks": seven({"title": "Empty day", "tasks": []}),
    "unknown task type": seven({"title": "Yoga", "tasks": [{"type": "yoga", "text": "Stretch"}]}),
    "blank task text": seven({"title": "Blank", "tasks": [{"type": "rest", "text": "   "}]}),
    "blank day title": seven({"title": " ", "tasks": [GOOD_TASK]}),
}


@pytest.mark.parametrize("answer", BAD_ANSWERS.values(), ids=BAD_ANSWERS.keys())
def test_unusable_llm_answer_triggers_the_fallback(make_client, answer):
    r = post(make_client(llm=FakeLLM(answer)))
    assert r.status_code == 201
    body = r.json()
    assert body["source"] == "fallback"
    assert len(body["days"]) == 7


@pytest.mark.parametrize("error", [RuntimeError("boom"), TimeoutError("too slow"), ConnectionError("offline")])
def test_llm_errors_trigger_the_fallback(make_client, error):
    r = post(make_client(llm=FakeLLM(error=error)))
    assert r.status_code == 201
    assert r.json()["source"] == "fallback"


def test_fallback_plan_has_the_right_number_of_days_and_dates(make_client):
    body = post(make_client(llm=FakeLLM(error=RuntimeError("boom"))), interview_date="2026-11-05").json()
    assert [d["date"] for d in body["days"]] == ["2026-11-02", "2026-11-03", "2026-11-04"]


def test_fallback_plan_mentions_the_company(make_client):
    body = post(make_client(llm=FakeLLM(error=RuntimeError("boom"))), company="Stripe").json()
    text = " ".join(d["title"] + " " + t["text"] for d in body["days"] for t in d["tasks"])
    assert "Stripe" in text


def test_the_llm_is_tried_three_times_before_giving_up(make_client):
    llm = FakeLLM(error=RuntimeError("boom"))
    post(make_client(llm=llm))
    assert len(llm.prompts) == 3


def test_failure_is_logged(make_client, caplog):
    with caplog.at_level(logging.WARNING, logger="ontarget.planner"):
        post(make_client(llm=FakeLLM(error=RuntimeError("boom"))))
    assert any("fallback" in r.getMessage().lower() and "boom" in r.getMessage() for r in caplog.records)


def test_error_details_are_not_leaked_to_the_user(make_client):
    r = post(make_client(llm=FakeLLM(error=RuntimeError("secret-api-key-123"))))
    assert "secret-api-key-123" not in r.text


def test_fallback_plan_is_saved_and_can_be_loaded(make_client):
    client = make_client(llm=FakeLLM(error=RuntimeError("boom")))
    created = post(client).json()
    assert client.get(f"/plans/{created['id']}").json() == created


def test_a_good_answer_after_a_bad_one_still_uses_the_llm(make_client):
    client = make_client(llm=FakeLLM(""))
    assert post(client).json()["source"] == "fallback"
    client = make_client(llm=FakeLLM(llm_plan_json(7)))
    assert post(client).json()["source"] == "llm"
