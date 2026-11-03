#!/usr/bin/env bash
# TDD helper that logs each red/green run to docs/tdd_log.md and commits.
#   scripts/tdd.sh red   <issue#> <test file> "<message>"   tests must FAIL, commits the tests
#   scripts/tdd.sh green <issue#> <test file> "<message>"   tests must PASS, commits with "Closes #N"
set -uo pipefail
cd "$(dirname "$0")/.."
mode=$1; n=$2; f=$3; msg=$4
out=$(python3 -m pytest "$f" -rN -p no:cacheprovider 2>&1); code=$?
line=$(echo "$out" | tail -1)
if [ "$mode" = red ] && [ $code -eq 0 ]; then echo "STOP: tests for #$n already pass, so they prove nothing"; exit 1; fi
if [ "$mode" = green ] && [ $code -ne 0 ]; then echo "$out" | tail -25; echo "STOP: tests for #$n still failing"; exit 1; fi
echo "- Issue #$n $mode: $line" >> docs/tdd_log.md
echo "$mode #$n: $line"
if [ "$mode" = green ]; then echo "  full suite: $(python3 -m pytest -rN -p no:cacheprovider 2>&1 | tail -1)"; fi
git add -A
if [ "$mode" = red ]; then git commit -qm "test(#$n): $msg (red)"; else git commit -qm "feat(#$n): $msg" -m "Closes #$n"; fi
