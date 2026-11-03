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
