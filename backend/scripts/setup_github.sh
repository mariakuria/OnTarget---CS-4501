#!/usr/bin/env bash
# Creates the GitHub repo, labels, milestone and the 9 issues, then pushes the code.
# Run on your own computer after `gh auth login`.   Usage: scripts/setup_github.sh [repo-name]
# The issues are created BEFORE the push so the "Closes #N" commit messages close them.
set -euo pipefail
NAME="${1:-ontarget-backend}"
cd "$(dirname "$0")/.."
git branch -M main
gh repo create "$NAME" --private --source=. --remote=origin
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Repo: $REPO"
for L in "backend:1d76db" "llm:8250df" "feature:0e8a16" "reliability:fbca04" "security:d93f0b"; do
  gh label create "${L%%:*}" --color "${L##*:}" --force
done
gh api "repos/$REPO/milestones" -f title="Alpha" -f description="OnTarget Alpha backend" >/dev/null
make_issue() { # number title labels file
  URL=$(gh issue create --title "$2" --label "$3" --milestone "Alpha" --body-file "$4")
  echo "$URL"
  case "$URL" in */issues/$1) ;; *) echo "WARNING: expected issue #$1 but got $URL. Commit messages say Closes #$1." ;; esac
}
make_issue 1 'Create a day-by-day plan from a company and interview date' "backend,feature" docs/issues/01-create-plan.md
make_issue 2 'Generate company-specific tasks with the LLM' "backend,llm,feature" docs/issues/02-llm-company-tasks.md
make_issue 3 'Fall back to a default plan when the LLM fails' "backend,llm,reliability" docs/issues/03-llm-fallback.md
make_issue 4 'Handle lesser-known and unusual company names safely' "backend,llm,security" docs/issues/04-odd-company-names.md
make_issue 5 'Save a plan and load it again later' "backend,feature" docs/issues/05-save-reload-plan.md
make_issue 6 'Mark tasks done and see my progress' "backend,feature" docs/issues/06-mark-task-done.md
make_issue 7 'Skip a day without hurting my progress' "backend,feature" docs/issues/07-skip-day.md
make_issue 8 'Open a coding problem with starter code' "backend,feature" docs/issues/08-open-problem.md
make_issue 9 'Use OnTarget in a web page served by the backend' "frontend,feature" docs/issues/09-web-page.md
git push -u origin main
echo "Done. Issues closed by the pushed commits:"
gh issue list --state all --milestone Alpha
