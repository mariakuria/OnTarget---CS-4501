"""Issue #2: generate company-specific tasks with the LLM."""
from types import SimpleNamespace

import pytest

from tests.fakes import FakeLLM, llm_plan_json

pytestmark = [pytest.mark.issue(2), pytest.mark.ai_generated]


def post(client, company="Amazon", interview_date="2026-11-09"):
    return client.post("/plans", json={"company": company, "interview_date": interview_date})


def test_valid_llm_answer_becomes_the_plan(make_client):
    r = post(make_client(llm=FakeLLM(llm_plan_json(7))))
    assert r.status_code == 201
    body = r.json()
    assert body["source"] == "llm"
    assert len(body["days"]) == 7
    assert body["days"][0]["title"] == "Amazon focus day 1"
    assert body["days"][0]["date"] == "2026-11-02"
    assert [t["id"] for t in body["days"][0]["tasks"]] == ["d1-t1", "d1-t2"]


def test_llm_is_called_exactly_once_per_plan(make_client):
    llm = FakeLLM(llm_plan_json(7))
    post(make_client(llm=llm))
    assert len(llm.prompts) == 1


def test_prompt_contains_company_day_count_and_problem_ids(make_client):
    from app.problems import PROBLEMS

    llm = FakeLLM(llm_plan_json(7))
    post(make_client(llm=llm))
    prompt = llm.prompts[0]
    assert "Amazon" in prompt
    assert "7-day" in prompt
    for problem_id in PROBLEMS:
        assert problem_id in prompt


def test_prompt_day_count_follows_the_interview_date(make_client):
    llm = FakeLLM(llm_plan_json(3))
    post(make_client(llm=llm), interview_date="2026-11-05")
    assert "3-day" in llm.prompts[0]


def test_json_in_a_code_fence_is_read(make_client):
    text = "```json\n" + llm_plan_json(7) + "\n```"
    assert post(make_client(llm=FakeLLM(text))).json()["source"] == "llm"


def test_json_surrounded_by_chatter_is_read(make_client):
    text = "Sure! Here is your plan:\n" + llm_plan_json(7) + "\nGood luck with the interview!"
    assert post(make_client(llm=FakeLLM(text))).json()["source"] == "llm"


def test_coding_task_keeps_its_problem_link(make_client):
    body = post(make_client(llm=FakeLLM(llm_plan_json(7)))).json()
    coding = body["days"][0]["tasks"][0]
    assert coding["type"] == "coding"
    assert coding["problem_id"] == "two-sum"
    assert body["days"][0]["tasks"][1]["problem_id"] is None


def test_unknown_problem_id_is_dropped_but_plan_still_works(make_client):
    body = post(make_client(llm=FakeLLM(llm_plan_json(7, problem_id="not-a-problem")))).json()
    assert body["source"] == "llm"
    assert all(t["problem_id"] is None for d in body["days"] for t in d["tasks"])


def test_llm_plan_progress_starts_at_zero(make_client):
    body = post(make_client(llm=FakeLLM(llm_plan_json(7)))).json()
    assert body["progress"] == {"done": 0, "total": 14, "percent": 0}


def test_llm_plan_is_saved(make_client):
    client = make_client(llm=FakeLLM(llm_plan_json(7)))
    created = post(client).json()
    assert client.get(f"/plans/{created['id']}").json() == created


def test_without_an_llm_the_default_plan_is_used(make_client):
    assert post(make_client(llm=None)).json()["source"] == "fallback"


# --- Anthropic client ---------------------------------------------------------


class StubAnthropic:
    def __init__(self, blocks):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._blocks = blocks

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=self._blocks)


def test_anthropic_client_sends_prompt_and_model_and_returns_text():
    from app.llm import AnthropicLLM

    stub = StubAnthropic([SimpleNamespace(type="text", text="hello")])
    out = AnthropicLLM(client=stub, model="test-model").complete("my prompt")
    assert out == "hello"
    call = stub.calls[0]
    assert call["model"] == "test-model"
    assert call["messages"] == [{"role": "user", "content": "my prompt"}]
    assert call["max_tokens"] > 0


def test_anthropic_client_joins_text_blocks_and_skips_other_blocks():
    from app.llm import AnthropicLLM

    blocks = [
        SimpleNamespace(type="text", text="part one "),
        SimpleNamespace(type="thinking", thinking="ignore me"),
        SimpleNamespace(type="text", text="part two"),
    ]
    assert AnthropicLLM(client=StubAnthropic(blocks)).complete("x") == "part one part two"


def test_anthropic_client_needs_an_api_key(monkeypatch):
    from app.llm import AnthropicLLM

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        AnthropicLLM()


def test_default_llm_is_none_without_a_key(monkeypatch):
    from app.llm import default_llm

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert default_llm() is None


def test_default_llm_is_built_when_a_key_is_set(monkeypatch):
    from app.llm import AnthropicLLM, default_llm

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert isinstance(default_llm(), AnthropicLLM)


def test_model_can_be_chosen_with_an_environment_variable(monkeypatch):
    from app.llm import AnthropicLLM

    monkeypatch.setenv("ONTARGET_MODEL", "my-model")
    stub = StubAnthropic([SimpleNamespace(type="text", text="ok")])
    AnthropicLLM(client=stub).complete("x")
    assert stub.calls[0]["model"] == "my-model"
