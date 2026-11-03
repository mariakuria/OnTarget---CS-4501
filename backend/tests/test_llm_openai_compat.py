"""Issue #2 (continued): any OpenAI-compatible LLM (Gemini, Groq, OpenRouter, Ollama) can write the plan."""
import httpx
import pytest

from tests.fakes import llm_plan_json

pytestmark = [pytest.mark.issue(2), pytest.mark.ai_generated]


def make_llm(handler, **kwargs):
    from app.llm import OpenAICompatibleLLM

    client = httpx.Client(transport=httpx.MockTransport(handler))
    return OpenAICompatibleLLM(client=client, **kwargs)


def reply(content):
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def test_sends_a_chat_completion_request_and_returns_the_text():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = request.read()
        return httpx.Response(200, json=reply("hello"))

    llm = make_llm(handler, base_url="https://example.test/v1", model="m1", api_key="k1")
    assert llm.complete("my prompt") == "hello"
    assert seen["url"] == "https://example.test/v1/chat/completions"
    assert seen["auth"] == "Bearer k1"
    assert b'"model":"m1"' in seen["body"].replace(b" ", b"")
    assert b"my prompt" in seen["body"]


def test_trailing_slash_in_the_base_url_is_fine():
    urls = []

    def handler(request):
        urls.append(str(request.url))
        return httpx.Response(200, json=reply("ok"))

    make_llm(handler, base_url="https://example.test/v1/", model="m").complete("x")
    assert urls == ["https://example.test/v1/chat/completions"]


def test_no_api_key_means_no_authorization_header():
    headers = []

    def handler(request):
        headers.append(request.headers.get("authorization"))
        return httpx.Response(200, json=reply("ok"))

    make_llm(handler, base_url="http://localhost:11434/v1", model="llama3.2").complete("x")
    assert headers == [None]


def test_http_errors_are_raised():
    llm = make_llm(lambda r: httpx.Response(401, json={"error": "bad key"}), base_url="https://e.test/v1", model="m")
    with pytest.raises(httpx.HTTPStatusError):
        llm.complete("x")


@pytest.mark.parametrize("body", [{}, {"choices": []}, {"choices": [{}]}, {"error": "rate limited"}])
def test_unexpected_response_shapes_raise_a_clear_error(body):
    llm = make_llm(lambda r: httpx.Response(200, json=body), base_url="https://e.test/v1", model="m")
    with pytest.raises(RuntimeError, match="unexpected"):
        llm.complete("x")


def test_empty_content_becomes_an_empty_string():
    llm = make_llm(lambda r: httpx.Response(200, json=reply(None)), base_url="https://e.test/v1", model="m")
    assert llm.complete("x") == ""


def test_default_llm_uses_the_openai_compatible_settings(monkeypatch):
    from app.llm import OpenAICompatibleLLM, default_llm

    monkeypatch.setenv("ONTARGET_LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("ONTARGET_LLM_MODEL", "some-model")
    monkeypatch.delenv("ONTARGET_LLM_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ignored-because-base-url-is-set")
    assert isinstance(default_llm(), OpenAICompatibleLLM)


def test_base_url_without_a_model_is_an_error(monkeypatch):
    from app.llm import default_llm

    monkeypatch.setenv("ONTARGET_LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.delenv("ONTARGET_LLM_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="ONTARGET_LLM_MODEL"):
        default_llm()


def test_default_llm_still_prefers_nothing_when_no_settings(monkeypatch):
    from app.llm import default_llm

    for name in ("ONTARGET_LLM_BASE_URL", "ONTARGET_LLM_MODEL", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert default_llm() is None


def test_a_plan_can_be_written_through_the_openai_compatible_client(make_client):
    llm = make_llm(
        lambda r: httpx.Response(200, json=reply("```json\n" + llm_plan_json(7) + "\n```")),
        base_url="https://e.test/v1",
        model="m",
    )
    body = make_client(llm=llm).post("/plans", json={"company": "Amazon", "interview_date": "2026-11-09"}).json()
    assert body["source"] == "llm"
    assert len(body["days"]) == 7
