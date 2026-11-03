"""Issue #7: skip a day without hurting progress."""
import pytest

pytestmark = [pytest.mark.issue(7), pytest.mark.ai_generated]

# Day 1 of the default plan has 3 tasks; the whole plan has 17.


def skip(client, plan, day_number, skipped=True):
    return client.patch(f"/plans/{plan['id']}/days/{day_number}", json={"skipped": skipped})


def mark(client, plan, task_id, done=True):
    return client.patch(f"/plans/{plan['id']}/tasks/{task_id}", json={"done": done})


def test_skipping_marks_only_that_day(client, new_plan):
    r = skip(client, new_plan, 2)
    assert r.status_code == 200
    flags = [d["skipped"] for d in r.json()["days"]]
    assert flags == [False, True, False, False, False, False, False]


def test_skipped_tasks_leave_the_total(client, new_plan):
    body = skip(client, new_plan, 1).json()
    assert body["progress"] == {"done": 0, "total": 14, "percent": 0}


def test_done_tasks_in_a_skipped_day_are_not_counted(client, new_plan):
    mark(client, new_plan, "d1-t1")
    mark(client, new_plan, "d2-t1")
    body = skip(client, new_plan, 1).json()
    assert body["progress"] == {"done": 1, "total": 14, "percent": 7}


def test_unskipping_brings_tasks_back(client, new_plan):
    mark(client, new_plan, "d1-t1")
    skip(client, new_plan, 1)
    body = skip(client, new_plan, 1, skipped=False).json()
    assert body["progress"] == {"done": 1, "total": 17, "percent": 6}
    assert body["days"][0]["skipped"] is False


def test_skipping_twice_is_the_same_as_once(client, new_plan):
    skip(client, new_plan, 1)
    assert skip(client, new_plan, 1).json()["progress"]["total"] == 14


def test_skipping_every_day_gives_zero_without_error(client, new_plan):
    for n in range(1, 8):
        body = skip(client, new_plan, n).json()
    assert body["progress"] == {"done": 0, "total": 0, "percent": 0}


def test_the_change_is_saved(client, new_plan):
    skip(client, new_plan, 3)
    saved = client.get(f"/plans/{new_plan['id']}").json()
    assert saved["days"][2]["skipped"] is True
    assert saved["progress"]["total"] == 15


@pytest.mark.parametrize("day_number", [0, 8, 99])
def test_unknown_day_number_returns_404(client, new_plan, day_number):
    assert skip(client, new_plan, day_number).status_code == 404


def test_unknown_plan_returns_404(client):
    r = client.patch("/plans/nope/days/1", json={"skipped": True})
    assert r.status_code == 404


def test_body_without_skipped_returns_422(client, new_plan):
    assert client.patch(f"/plans/{new_plan['id']}/days/1", json={}).status_code == 422


def test_non_numeric_day_returns_422(client, new_plan):
    assert client.patch(f"/plans/{new_plan['id']}/days/abc", json={"skipped": True}).status_code == 422
