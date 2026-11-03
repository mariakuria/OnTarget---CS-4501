"""Issue #6: mark tasks done and see progress."""
import pytest

pytestmark = [pytest.mark.issue(6), pytest.mark.ai_generated]

# The default 7-day plan has 3+2+2+3+2+2+3 = 17 tasks.
TOTAL = 17


def task_ids(plan):
    return [t["id"] for d in plan["days"] for t in d["tasks"]]


def mark(client, plan, task_id, done=True):
    return client.patch(f"/plans/{plan['id']}/tasks/{task_id}", json={"done": done})


def test_new_plan_starts_at_zero_progress(new_plan):
    assert new_plan["progress"] == {"done": 0, "total": TOTAL, "percent": 0}


def test_marking_a_task_done_updates_the_task_and_progress(client, new_plan):
    first = task_ids(new_plan)[0]
    r = mark(client, new_plan, first)
    assert r.status_code == 200
    body = r.json()
    assert body["days"][0]["tasks"][0]["done"] is True
    assert body["progress"] == {"done": 1, "total": TOTAL, "percent": 6}


def test_percent_is_rounded_to_the_nearest_whole_number(client, new_plan):
    for tid in task_ids(new_plan)[:9]:
        body = mark(client, new_plan, tid).json()
    assert body["progress"] == {"done": 9, "total": TOTAL, "percent": 53}


def test_all_tasks_done_is_100_percent(client, new_plan):
    for tid in task_ids(new_plan):
        body = mark(client, new_plan, tid).json()
    assert body["progress"]["percent"] == 100


def test_a_task_can_be_unmarked(client, new_plan):
    first = task_ids(new_plan)[0]
    mark(client, new_plan, first, True)
    body = mark(client, new_plan, first, False).json()
    assert body["days"][0]["tasks"][0]["done"] is False
    assert body["progress"]["done"] == 0


def test_marking_the_same_task_twice_counts_once(client, new_plan):
    first = task_ids(new_plan)[0]
    mark(client, new_plan, first)
    assert mark(client, new_plan, first).json()["progress"]["done"] == 1


def test_only_the_chosen_task_changes(client, new_plan):
    ids = task_ids(new_plan)
    body = mark(client, new_plan, ids[2]).json()
    done = [t["id"] for d in body["days"] for t in d["tasks"] if t["done"]]
    assert done == [ids[2]]


def test_the_change_is_saved(client, new_plan):
    first = task_ids(new_plan)[0]
    mark(client, new_plan, first)
    saved = client.get(f"/plans/{new_plan['id']}").json()
    assert saved["days"][0]["tasks"][0]["done"] is True
    assert saved["progress"]["done"] == 1


def test_unknown_task_returns_404(client, new_plan):
    assert mark(client, new_plan, "d99-t1").status_code == 404


def test_unknown_plan_returns_404(client):
    r = client.patch("/plans/nope/tasks/d1-t1", json={"done": True})
    assert r.status_code == 404


def test_body_without_done_returns_422(client, new_plan):
    r = client.patch(f"/plans/{new_plan['id']}/tasks/d1-t1", json={})
    assert r.status_code == 422


def test_non_boolean_done_returns_422(client, new_plan):
    r = client.patch(f"/plans/{new_plan['id']}/tasks/d1-t1", json={"done": "maybe"})
    assert r.status_code == 422
