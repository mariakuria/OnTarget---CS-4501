from datetime import date

import pytest
from fastapi.testclient import TestClient

TODAY = date(2026, 11, 2)


@pytest.fixture(autouse=True)
def clean_llm_environment(monkeypatch):
    """Tests must never depend on, or spend, the LLM settings in the developer's terminal."""
    for name in ("ONTARGET_LLM_BASE_URL", "ONTARGET_LLM_MODEL", "ONTARGET_LLM_API_KEY",
                 "ANTHROPIC_API_KEY", "ONTARGET_MODEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch):
    """Retries wait between attempts in real life; tests should not."""
    import app.planner as planner

    monkeypatch.setattr(planner, "RETRY_DELAY_SECONDS", 0, raising=False)


@pytest.fixture
def today():
    return TODAY


@pytest.fixture
def make_client():
    """Build a test client around a fresh app. Imports the app lazily."""
    from app.main import create_app

    def _make(llm=None, store=None, today=TODAY):
        return TestClient(create_app(llm=llm, store=store, today_fn=lambda: today))

    return _make


@pytest.fixture
def client(make_client):
    return make_client()


@pytest.fixture
def new_plan(client):
    """Create a 7-day plan (interview one week after TODAY) and return the JSON."""
    r = client.post("/plans", json={"company": "Amazon", "interview_date": "2026-11-09"})
    assert r.status_code == 201, r.text
    return r.json()
