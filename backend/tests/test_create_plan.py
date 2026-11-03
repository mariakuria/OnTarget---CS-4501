"""Issue #1: create a day-by-day plan from a company and interview date."""
import pytest

pytestmark = [pytest.mark.issue(1), pytest.mark.ai_generated]


def post(client, company="Amazon", interview_date="2026-11-09"):
    return client.post("/plans", json={"company": company, "interview_date": interview_date})


def test_valid_request_returns_201_with_plan(client):
    r = post(client)
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert body["company"] == "Amazon"
    assert body["interview_date"] == "2026-11-09"


def test_one_day_per_day_until_interview(new_plan):
    assert len(new_plan["days"]) == 7


def test_last_day_is_day_before_interview(new_plan):
    assert new_plan["days"][0]["date"] == "2026-11-02"
    assert new_plan["days"][-1]["date"] == "2026-11-08"


@pytest.mark.manual
def test_one_day_plan_is_the_day_before_the_interview(client):
    response = post(client, interview_date="2026-11-03")
    assert response.status_code == 201
    body = response.json()
    assert len(body["days"]) == 1
    assert body["days"][0]["date"] == "2026-11-02"


def test_day_numbers_start_at_one(new_plan):
    assert [d["number"] for d in new_plan["days"]] == list(range(1, 8))


@pytest.mark.parametrize(
    "interview_date,expected_days",
    [("2026-11-03", 1), ("2026-11-05", 3), ("2026-11-16", 14), ("2026-12-31", 14)],
)
def test_day_count_is_days_until_interview_capped_at_14(client, interview_date, expected_days):
    r = post(client, interview_date=interview_date)
    assert r.status_code == 201
    assert len(r.json()["days"]) == expected_days


def test_far_away_interview_plans_the_last_14_days(client):
    days = post(client, interview_date="2026-12-31").json()["days"]
    assert days[0]["date"] == "2026-12-17"
    assert days[-1]["date"] == "2026-12-30"


def test_every_day_has_a_task_and_no_task_starts_done(new_plan):
    for day in new_plan["days"]:
        assert day["title"]
        assert len(day["tasks"]) >= 1
        for task in day["tasks"]:
            assert task["text"]
            assert task["done"] is False


def test_task_ids_are_unique(new_plan):
    ids = [t["id"] for d in new_plan["days"] for t in d["tasks"]]
    assert len(ids) == len(set(ids))


def test_company_is_trimmed(client):
    assert post(client, company="  Amazon  ").json()["company"] == "Amazon"


def test_company_of_exactly_80_characters_is_accepted(client):
    assert post(client, company="x" * 80).status_code == 201


@pytest.mark.parametrize("company", ["", "   ", "x" * 81])
def test_blank_or_too_long_company_is_rejected(client, company):
    assert post(client, company=company).status_code == 422


def test_missing_company_is_rejected(client):
    assert client.post("/plans", json={"interview_date": "2026-11-09"}).status_code == 422


@pytest.mark.parametrize("interview_date", ["2026-11-02", "2026-11-01", "2020-01-01"])
def test_today_or_past_date_is_rejected(client, interview_date):
    r = post(client, interview_date=interview_date)
    assert r.status_code == 422
    assert "future" in r.json()["detail"]


@pytest.mark.parametrize("interview_date", ["not-a-date", "2026-13-40", ""])
def test_invalid_date_is_rejected(client, interview_date):
    assert post(client, interview_date=interview_date).status_code == 422


def test_missing_date_is_rejected(client):
    assert client.post("/plans", json={"company": "Amazon"}).status_code == 422
