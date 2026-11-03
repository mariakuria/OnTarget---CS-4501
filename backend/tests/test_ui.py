"""Issue #9: use OnTarget in a web page served by the backend."""
import pytest

pytestmark = [pytest.mark.issue(9), pytest.mark.ai_generated]


def test_home_page_is_the_app(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "OnTarget" in r.text


def test_home_page_has_the_company_and_date_form(client):
    html = client.get("/").text
    assert 'id="company"' in html
    assert 'id="date"' in html
    assert "Build my plan" in html


def test_home_page_talks_to_the_same_server(client):
    html = client.get("/").text
    assert "/plans" in html
    assert "/problems/" in html
    assert "http://" not in html.replace("http://www.w3.org", "")  # no hardcoded server address


def test_home_page_needs_no_external_scripts(client):
    assert "<script src" not in client.get("/").text.lower()


def test_api_and_docs_still_work_next_to_the_page(client, new_plan):
    assert client.get(f"/plans/{new_plan['id']}").json()["id"] == new_plan["id"]
    assert client.get("/problems").status_code == 200
    assert client.get("/docs").status_code == 200


def test_unknown_plan_is_still_a_json_404(client):
    r = client.get("/plans/nope")
    assert r.status_code == 404
    assert r.json()["detail"] == "Plan not found"


def test_unknown_page_returns_404(client):
    assert client.get("/nothing-here").status_code == 404


@pytest.mark.manual
@pytest.mark.issue(1)
@pytest.mark.issue(6)
@pytest.mark.issue(7)
@pytest.mark.issue(8)
def test_candidate_can_build_open_and_update_a_plan_from_the_served_app(client):
    assert client.get("/").status_code == 200

    created_response = client.post(
        "/plans", json={"company": "Amazon", "interview_date": "2026-11-09"}
    )
    assert created_response.status_code == 201
    created = created_response.json()

    coding_day = next(
        day
        for day in created["days"]
        if any(task["type"] == "coding" and task["problem_id"] for task in day["tasks"])
    )
    coding_task = next(
        task for task in coding_day["tasks"] if task["type"] == "coding" and task["problem_id"]
    )
    problem_response = client.get(f"/problems/{coding_task['problem_id']}")
    assert problem_response.status_code == 200
    assert problem_response.json()["starter_code"]

    completed = client.patch(
        f"/plans/{created['id']}/tasks/{coding_task['id']}", json={"done": True}
    )
    assert completed.status_code == 200
    assert completed.json()["progress"]["done"] == 1

    skipped_day = next(
        day for day in created["days"] if day["number"] != coding_day["number"]
    )
    skipped = client.patch(
        f"/plans/{created['id']}/days/{skipped_day['number']}",
        json={"skipped": True},
    )
    assert skipped.status_code == 200
    assert skipped.json()["days"][skipped_day["number"] - 1]["skipped"] is True
    assert skipped.json()["progress"]["done"] == 1

    saved = client.get(f"/plans/{created['id']}")
    assert saved.status_code == 200
    assert saved.json() == skipped.json()
