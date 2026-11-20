#!/usr/bin/env bash
# Rebuilds fixtures/synthetic: one commit holding an added empty file, a binary
# edit, a pure rename and a lone mode change — the four changes git reports with
# no @@ hunk. Same shapes as the PER-36 block in tests/run-tests.sh.
# Usage: build.sh <repo-root> <scratch-dir>
set -euo pipefail
root=$1 w=$2 A=$2/repo
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
git init -q -b main "$A"; cd "$A"; git config user.email t@t; git config user.name t
bin() { { printf 'PNG'; printf 'x' | tr 'x' '\000'; printf '%s' "$2"; } > "$1"; }
printf 'old\n' > old.txt; printf '#!/bin/sh\necho hi\n' > tool.sh; bin logo.png aaa
git add -A; git commit -qm base
bin logo.png bbbb; : > empty.txt; git mv old.txt renamed.txt; chmod +x tool.sh
git add -A; git commit -qm change
S=$root/skills/engineering-manager/scripts
BUILD_DIR=$S/review-packet KK_REVIEW_PACKET_NOW=2026-11-04T00:00:00Z KK_REVIEW_PACKET_ROOT=$w/out \
  bash "$S/kk-review-packet.sh" build --ticket PER-175 --repo "$A" --base HEAD~1 --no-merge-base
