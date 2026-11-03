#!/usr/bin/env bash
# Adds this backend to an EXISTING team repo (in a backend/ folder, on its own branch), creates the 8 issues
# there, and opens a pull request that closes them when it is merged. Nothing in the team repo is overwritten.
#
# Usage (from this repo's folder, after `gh auth login`):
#   scripts/push_to_team_repo.sh https://github.com/OWNER/REPO
set -euo pipefail

URL="${1:?Usage: scripts/push_to_team_repo.sh https://github.com/OWNER/REPO}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(echo "$URL" | sed -E 's#^https?://github.com/##; s#\.git$##; s#/$##')"
BRANCH="backend-alpha"
CLONE="$SRC/../$(basename "$REPO")-team-clone"

command -v gh >/dev/null || { echo "Install the GitHub CLI first: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "You are not logged in. Run: gh auth login"; exit 1; }
[ -e "$CLONE" ] && { echo "$CLONE already exists. Rename or delete it, then run this again."; exit 1; }

PERM="$(gh repo view "$REPO" --json viewerPermission -q .viewerPermission)"
case "$PERM" in
  WRITE|MAINTAIN|ADMIN) ;;
  *) echo "You only have '$PERM' access to $REPO. Ask the repo owner to add you as a collaborator"
     echo "(repo Settings > Collaborators), accept the email invite, then run this again."; exit 1 ;;
esac
BASE="$(gh repo view "$REPO" --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)"
BASE="${BASE:-main}"

echo "== Cloning $REPO"
gh repo clone "$REPO" "$CLONE"
cd "$CLONE"
EMPTY=0
git rev-parse HEAD >/dev/null 2>&1 || EMPTY=1
if [ "$EMPTY" = 1 ]; then git checkout -q -B "$BASE"; else git checkout -q -b "$BRANCH"; fi

echo "== Copying the backend into backend/"
mkdir -p backend
(cd "$SRC" && tar --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache \
  --exclude='*.db' --exclude=coverage.json --exclude=htmlcov -cf - .) | tar -xf - -C backend

echo "== Creating labels, milestone and issues in $REPO"
for L in "backend:1d76db" "llm:8250df" "feature:0e8a16" "reliability:fbca04" "security:d93f0b"; do
  gh label create "${L%%:*}" --color "${L##*:}" --force --repo "$REPO" >/dev/null
done
gh api "repos/$REPO/milestones" -f title="Alpha" -f description="OnTarget Alpha backend" >/dev/null 2>&1 || true

NUMS=()
make_issue() { # title labels file
  local body url
  body="$(mktemp)"
  sed 's#`tests/#`backend/tests/#g' "$SRC/docs/issues/$3" > "$body"
  url="$(gh issue create --repo "$REPO" --title "$1" --label "$2" --milestone "Alpha" --body-file "$body")"
  rm -f "$body"
  echo "  $url"
  NUMS+=("${url##*/}")
}
make_issue 'Create a day-by-day plan from a company and interview date' "backend,feature" 01-create-plan.md
make_issue 'Generate company-specific tasks with the LLM' "backend,llm,feature" 02-llm-company-tasks.md
make_issue 'Fall back to a default plan when the LLM fails' "backend,llm,reliability" 03-llm-fallback.md
make_issue 'Handle lesser-known and unusual company names safely' "backend,llm,security" 04-odd-company-names.md
make_issue 'Save a plan and load it again later' "backend,feature" 05-save-reload-plan.md
make_issue 'Mark tasks done and see my progress' "backend,feature" 06-mark-task-done.md
make_issue 'Skip a day without hurting my progress' "backend,feature" 07-skip-day.md
make_issue 'Open a coding problem with starter code' "backend,feature" 08-open-problem.md

git add backend
git commit -q -m "Add OnTarget backend (Alpha)" \
  -m "FastAPI backend with LLM-written interview prep plans. Tests: backend/tests. Run: cd backend && python -m pytest"

if [ "$EMPTY" = 1 ]; then
  echo "== The repo was empty, so pushing to $BASE and closing the issues"
  git push -q -u origin "$BASE"
  for n in "${NUMS[@]}"; do
    gh issue close "$n" --repo "$REPO" --comment "Implemented in backend/ with tests." >/dev/null
  done
  echo "Done: https://github.com/$REPO"
else
  git push -q -u origin "$BRANCH"
  BODY="Adds the OnTarget backend in backend/ (FastAPI, LLM plan generation with retry and fallback, SQLite, tests).
Run it: cd backend && pip install -r requirements.txt && python -m pytest

"
  for n in "${NUMS[@]}"; do BODY+="Closes #$n"$'\n'; done
  PR="$(gh pr create --repo "$REPO" --base "$BASE" --head "$BRANCH" --title "Add OnTarget backend (Alpha)" --body "$BODY")"
  echo "== Pull request: $PR"
  echo "Merge it (or ask a teammate to) so issues #${NUMS[0]} to #${NUMS[${#NUMS[@]}-1]} close."
fi
