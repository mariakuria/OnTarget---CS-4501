"""Issue #5: save a plan and load it again later."""
import os

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.issue(5), pytest.mark.ai_generated]


def create(client, company="Amazon", interview_date="2026-11-09"):
    return client.post("/plans", json={"company": company, "interview_date": interview_date}).json()


def test_get_returns_the_plan_that_post_returned(client, new_plan):
    r = client.get(f"/plans/{new_plan['id']}")
    assert r.status_code == 200
    assert r.json() == new_plan


def test_unknown_plan_returns_404(client):
    r = client.get("/plans/nope")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_each_plan_gets_a_different_id(client):
    assert create(client)["id"] != create(client)["id"]


def test_plan_survives_an_app_restart(make_client, tmp_path):
    from app.store import SqliteStore

    db = str(tmp_path / "plans.db")
    created = create(make_client(store=SqliteStore(db)))
    reloaded = make_client(store=SqliteStore(db)).get(f"/plans/{created['id']}")
    assert reloaded.status_code == 200
    assert reloaded.json() == created


@pytest.mark.manual
def test_task_and_skip_updates_survive_an_app_restart(make_client, tmp_path):
    from app.store import SqliteStore

    db = str(tmp_path / "plans.db")
    first_app = make_client(store=SqliteStore(db))
    created = create(first_app)
    task = created["days"][0]["tasks"][0]
    completed = first_app.patch(
        f"/plans/{created['id']}/tasks/{task['id']}", json={"done": True}
    )
    assert completed.status_code == 200
    skipped = first_app.patch(
        f"/plans/{created['id']}/days/2", json={"skipped": True}
    )
    assert skipped.status_code == 200
    expected = skipped.json()

    restarted_app = make_client(store=SqliteStore(db))
    response = restarted_app.get(f"/plans/{created['id']}")
    assert response.status_code == 200
    assert response.json() == expected


def test_sqlite_store_round_trip_keeps_dates_and_tasks(tmp_path):
    from app import planner
    from app.store import SqliteStore
    import datetime as dt

    store = SqliteStore(str(tmp_path / "plans.db"))
    plan = planner.create_plan("Amazon", dt.date(2026, 11, 9), dt.date(2026, 11, 2))
    store.save(plan)
    assert store.get(plan.id) == plan


def test_sqlite_store_returns_none_for_missing_plan(tmp_path):
    from app.store import SqliteStore

    assert SqliteStore(str(tmp_path / "plans.db")).get("missing") is None


def test_saving_the_same_plan_again_overwrites_it(tmp_path):
    from app import planner
    from app.store import SqliteStore
    import datetime as dt

    store = SqliteStore(str(tmp_path / "plans.db"))
    plan = planner.create_plan("Amazon", dt.date(2026, 11, 9), dt.date(2026, 11, 2))
    store.save(plan)
    plan.days[0].tasks[0].done = True
    store.save(plan)
    assert store.get(plan.id).days[0].tasks[0].done is True


def test_default_server_app_saves_to_the_database_file(monkeypatch, tmp_path):
    from app.server import build_app

    db = tmp_path / "server.db"
    monkeypatch.setenv("ONTARGET_DB", str(db))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = TestClient(build_app())
    r = client.post("/plans", json={"company": "Amazon", "interview_date": "2999-01-01"})
    assert r.status_code == 201
    assert os.path.exists(db)
    assert client.get(f"/plans/{r.json()['id']}").status_code == 200
