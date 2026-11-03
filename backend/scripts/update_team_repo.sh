#!/usr/bin/env bash
# Adds the web UI (story 9) to the team repo: new branch, refreshed backend/ folder, one new issue, one pull request.
# Usage (from this repo's folder, after `gh auth login`):  scripts/update_team_repo.sh https://github.com/OWNER/REPO
set -euo pipefail
URL="${1:?Usage: scripts/update_team_repo.sh https://github.com/OWNER/REPO}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(echo "$URL" | sed -E 's#^https?://github.com/##; s#\.git$##; s#/$##')"
BRANCH="backend-ui"
CLONE="$SRC/../$(basename "$REPO")-ui-clone"
command -v gh >/dev/null || { echo "Install the GitHub CLI first: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Not logged in. Run: gh auth login"; exit 1; }
[ -e "$CLONE" ] && { echo "$CLONE already exists. Rename or delete it, then run again."; exit 1; }
BASE="$(gh repo view "$REPO" --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)"; BASE="${BASE:-main}"

gh repo clone "$REPO" "$CLONE"; cd "$CLONE"
git checkout -q -b "$BRANCH"
mkdir -p backend
(cd "$SRC" && tar --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache \
  --exclude='*.db' --exclude=coverage.json --exclude=htmlcov -cf - .) | tar -xf - -C backend

gh label create frontend --color c5def5 --force --repo "$REPO" >/dev/null
BODY="$(mktemp)"; sed 's#`tests/#`backend/tests/#g' "$SRC/docs/issues/09-web-page.md" > "$BODY"
ISSUE="$(gh issue create --repo "$REPO" --title 'Use OnTarget in a web page served by the backend' --label "frontend,feature" --milestone Alpha --body-file "$BODY")"
rm -f "$BODY"; N="${ISSUE##*/}"; echo "Issue: $ISSUE"

git add backend
git commit -q -m "Add web UI served by the backend (story 9)" -m "Closes #$N"
git push -q -u origin "$BRANCH"
PR="$(gh pr create --repo "$REPO" --base "$BASE" --head "$BRANCH" --title "Add web UI (story 9)" --body "Adds the page at / (backend/app/static/index.html), tests in backend/tests/test_ui.py, updated docs.
Run: cd backend && uvicorn app.server:build_app --factory, then open http://127.0.0.1:8000/

Closes #$N")"
echo "Pull request: $PR"
