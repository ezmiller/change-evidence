#!/usr/bin/env bash
# Rebuilds fixtures/edge-cases, the cases PER-176 leaves open.
#   change:   submodule added and bumped, rename with edit, deleted empty file,
#             CRLF-only change, a path with a space, a lockfile → packet.json
#   typechg:  file → symlink, which the current build refuses → typechange.txt
# Usage: build.sh <repo-root> <scratch-dir>
set -euo pipefail
root=$1 w=$2 A=$2/repo S=$2/sub out=$1/docs/change-evidence/fixtures/edge-cases
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_DATE=2026-11-04T00:00:00Z GIT_COMMITTER_DATE=2026-11-04T00:00:00Z
git init -q -b main "$S"; (cd "$S"; git config user.email t@t; git config user.name t
  echo one > a; git add a; git commit -qm one; echo two > a; git commit -qam two)
git init -q -b main "$A"; cd "$A"; git config user.email t@t; git config user.name t
sub() { git -c protocol.file.allow=always submodule add -q "$S" "$1"
  git config -f .gitmodules "submodule.$1.url" https://example.invalid/sub.git; }
sub moved-sub; (cd moved-sub; git checkout -q HEAD~1)
printf 'a\nb\nc\nd\ne\nf\n' > keep.txt; : > gone.txt; printf 'x\ny\n' > crlf.txt
printf 'target\n' > target.txt; printf 'real\n' > link-me; printf 'v1\n' > 'with space.txt'
printf 'lock 1\n' > flake.lock
git add -A; git commit -qm base
sub new-sub; (cd moved-sub; git checkout -q main)
git mv keep.txt kept.txt; printf 'a\nb\nc\nd\ne\nF\n' > kept.txt
git rm -q gone.txt; printf 'x\r\ny\r\n' > crlf.txt
printf 'v2\n' > 'with space.txt'; printf 'lock 2\n' > flake.lock
git add -A; git commit -qm change
rm link-me; ln -s target.txt link-me; git add -A; git commit -qm typechg
range() { git diff --no-color --no-ext-diff --no-textconv --find-renames --unified=3 "$@"; }
range HEAD~2 HEAD~1 > "$out/raw.diff"
git diff --raw -z --no-abbrev --find-renames HEAD~2 HEAD~1 | tr '\0' '\n' > "$out/raw-records.txt"
P=$root/skills/engineering-manager/scripts
build() { BUILD_DIR=$P/review-packet KK_REVIEW_PACKET_NOW=2026-11-04T00:00:00Z KK_REVIEW_PACKET_ROOT=$w/out \
  bash "$P/kk-review-packet.sh" build --ticket PER-176 --repo "$A" --no-merge-base "$@"; }
dir=$(build --base HEAD~2 --head HEAD~1); cp "$dir/packet.json" "$out/packet.json"
{ echo '$ git diff --raw -z HEAD~1 HEAD | tr "\0" "\n"'; git diff --raw -z --find-renames HEAD~1 HEAD | tr '\0' '\n'
  echo '$ git diff HEAD~1 HEAD | grep "^diff --git"'; range HEAD~1 HEAD | grep '^diff --git'
  echo '$ kk-review-packet build --base HEAD~1 --head HEAD'; build --base HEAD~1 --head HEAD 2>&1 || echo "exit $?"
} > "$out/typechange.txt"
