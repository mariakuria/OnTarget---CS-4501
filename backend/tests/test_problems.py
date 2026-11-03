"""Issue #8: open a coding problem with starter code."""
import re

import pytest

pytestmark = [pytest.mark.issue(8), pytest.mark.ai_generated]

LANGS = ["Python", "Java", "C++", "JavaScript"]
IDS = ["two-sum", "top-k-words", "merge-intervals", "num-islands", "rotting-oranges", "meeting-rooms", "trap-water"]


def test_list_returns_the_seven_catalog_problems(client):
    r = client.get("/problems")
    assert r.status_code == 200
    items = r.json()
    assert sorted(p["id"] for p in items) == sorted(IDS)
    for p in items:
        assert p["title"]
        assert p["difficulty"] in ("Easy", "Medium", "Hard")


def test_get_problem_returns_details(client):
    r = client.get("/problems/two-sum")
    assert r.status_code == 200
    p = r.json()
    assert p["title"] == "Two Sum"
    assert p["difficulty"] == "Easy"
    assert p["topics"]
    assert p["description"]
    assert p["constraints"]
    assert p["examples"][0]["input"] and p["examples"][0]["output"]


@pytest.mark.parametrize("problem_id", IDS)
def test_every_problem_is_complete(client, problem_id):
    p = client.get(f"/problems/{problem_id}").json()
    assert p["id"] == problem_id
    assert len(p["examples"]) >= 1
    assert all(e["input"] and e["output"] for e in p["examples"])
    assert p["constraints"]
    assert sorted(p["starter_code"]) == sorted(LANGS)
    assert all(code.strip() for code in p["starter_code"].values())


def test_starter_code_matches_each_language(client):
    code = client.get("/problems/two-sum").json()["starter_code"]
    assert "def twoSum(self, nums: list[int], target: int)" in code["Python"]
    assert "class Solution" in code["Java"] and "int[] twoSum(int[] nums, int target)" in code["Java"]
    assert "vector<int> twoSum(vector<int>& nums, int target)" in code["C++"]
    assert "var twoSum = function(nums, target)" in code["JavaScript"]


def test_unknown_problem_returns_404(client):
    r = client.get("/problems/does-not-exist")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_problem_ids_are_lowercase_slugs(client):
    for p in client.get("/problems").json():
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", p["id"])


def test_problem_ids_in_a_new_plan_exist_in_the_catalog(client, new_plan):
    linked = [t["problem_id"] for d in new_plan["days"] for t in d["tasks"] if t["problem_id"]]
    assert linked
    for problem_id in linked:
        assert client.get(f"/problems/{problem_id}").status_code == 200


def test_every_coding_task_in_a_new_plan_has_a_problem(new_plan):
    coding = [t for d in new_plan["days"] for t in d["tasks"] if t["type"] == "coding"]
    assert coding
    assert all(t["problem_id"] for t in coding)
