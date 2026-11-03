#!/usr/bin/env python3
"""Engineering metrics for the Alpha slide.  Run from the repo root:  python3 scripts/metrics.py

Tests are grouped by their @pytest.mark.issue(n) marker. A test counts as AI-generated unless it
carries @pytest.mark.manual (put that on tests you wrote or substantially edited yourself).
"""
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class Collector:
    def __init__(self):
        self.tests = {}  # nodeid -> dict(issue, manual, outcome)

    def pytest_collection_modifyitems(self, items):
        for item in items:
            issue = item.get_closest_marker("issue")
            self.tests[item.nodeid] = {
                "issue": issue.args[0] if issue else None,
                "manual": item.get_closest_marker("manual") is not None,
                "outcome": "not run",
            }

    def pytest_runtest_logreport(self, report):
        t = self.tests.get(report.nodeid)
        if not t:
            return
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
            t["outcome"] = report.outcome


def issue_counts():
    """(logged, closed). Uses `gh` if it is logged in to this repo, otherwise local files and commits."""
    if shutil.which("gh"):
        r = subprocess.run(["gh", "issue", "list", "--state", "all", "--limit", "200", "--json", "state"],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode == 0:
            states = [i["state"] for i in json.loads(r.stdout)]
            return len(states), states.count("CLOSED"), "GitHub"
    logged = len(list((ROOT / "docs" / "issues").glob("[0-9]*.md")))
    log = subprocess.run(["git", "log", "--format=%B"], capture_output=True, text=True, cwd=ROOT).stdout
    closed = len(set(re.findall(r"^Closes #(\d+)", log, re.M)))
    return logged, closed, "local files and 'Closes #N' commits"


def main():
    collector = Collector()
    pytest.main(["-q", "-p", "no:cacheprovider", "--cov=app", "--cov-report=json:coverage.json",
                 "--cov-report=term-missing:skip-covered"], plugins=[collector])
    tests = collector.tests
    total = len(tests)
    passed = sum(1 for t in tests.values() if t["outcome"] == "passed")
    per_issue = Counter(t["issue"] for t in tests.values())
    manual = sum(1 for t in tests.values() if t["manual"])
    ai = total - manual
    stories = len(re.findall(r"^## Story", (ROOT / "docs" / "user_stories.md").read_text(), re.M))
    logged, closed, source = issue_counts()
    cov = json.loads((ROOT / "coverage.json").read_text())["totals"]["percent_covered"]
    untagged = per_issue.get(None, 0)

    by_issue = defaultdict(lambda: [0, 0])
    for t in tests.values():
        by_issue[t["issue"]][0] += 1
        by_issue[t["issue"]][1] += t["outcome"] == "passed"

    out = [
        "", "# Engineering metrics", "",
        "| Metric | Value |", "|---|---|",
        f"| User stories | {stories} |",
        f"| GitHub issues logged / closed | {logged} / {closed} ({source}) |",
        f"| Automated tests | {total} |",
        f"| Average tests per issue | {total / max(logged, 1):.1f} |",
        f"| Test pass rate | {100 * passed / max(total, 1):.1f}% ({passed}/{total}) |",
        f"| Line coverage | {cov:.1f}% |",
        f"| AI-generated vs manually refined tests | {ai} vs {manual} ({100 * ai / max(total, 1):.0f}% / {100 * manual / max(total, 1):.0f}%) |",
        "", "## Tests per issue", "", "| Issue | Tests | Passing |", "|---|---|---|",
    ]
    for n in sorted(k for k in by_issue if k is not None):
        out.append(f"| #{n} | {by_issue[n][0]} | {by_issue[n][1]} |")
    if untagged:
        out.append(f"\nWARNING: {untagged} tests have no @pytest.mark.issue(n) marker.")
    if manual == 0:
        out.append("\nNote: no test is marked @pytest.mark.manual yet. Mark the tests you write or change yourself.")
    text = "\n".join(out)
    print(text)
    (ROOT / "docs" / "metrics.md").write_text(text.lstrip() + "\n")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
