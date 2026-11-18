#!/bin/sh
# Install Foundathyon skills for Cursor, Codex, GitHub Copilot and any agent
# that reads the Agent Skills format from ~/.agents/skills (Claude Code
# installs them with /plugin instead).
#
#   curl -fsSL https://raw.githubusercontent.com/fundathyon/marketplace/main/scripts/install.sh | sh -s -- accounts
#   sh scripts/install.sh platform accounts cron-jobs   # several products
#   sh scripts/install.sh all                           # every plugin
#   sh scripts/install.sh --list                        # what there is
#
# Options:
#   --dest DIR   where to install (default: ~/.agents/skills; use
#                .agents/skills to install into the current repository)
#   --from DIR   install from a local checkout instead of downloading
#   --ref REF    branch or tag to download (default: main)
#   --list       list the plugins and their skills, then exit
#
# Every skill folder is replaced as a whole, so files removed upstream do not
# linger. POSIX sh, curl and tar only. Exits non-zero on any failure.
set -eu

REPO="fundathyon/marketplace"
DEST="${HOME}/.agents/skills"
FROM=""
REF="main"
LIST=0
PLUGINS=""

die() { echo "install.sh: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dest) [ $# -ge 2 ] || die "--dest needs a directory"; DEST="$2"; shift 2 ;;
    --from) [ $# -ge 2 ] || die "--from needs a directory"; FROM="$2"; shift 2 ;;
    --ref) [ $# -ge 2 ] || die "--ref needs a branch or tag"; REF="$2"; shift 2 ;;
    --list) LIST=1; shift ;;
    -h|--help) sed -n '2,20p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) PLUGINS="$PLUGINS $1"; shift ;;
  esac
done

WORK=""
cleanup() { if [ -n "$WORK" ]; then rm -rf "$WORK"; fi; }
trap cleanup EXIT INT TERM

if [ -n "$FROM" ]; then
  ROOT="$FROM"
else
  command -v curl >/dev/null 2>&1 || die "curl is required"
  command -v tar >/dev/null 2>&1 || die "tar is required"
  WORK="$(mktemp -d)"
  curl -fsSL "https://codeload.github.com/${REPO}/tar.gz/${REF}" | tar -xz -C "$WORK" \
    || die "could not download ${REPO}@${REF}"
  ROOT="$(find "$WORK" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
fi
[ -d "$ROOT/plugins" ] || die "$ROOT is not a Foundathyon marketplace (no plugins/)"

if [ "$LIST" -eq 1 ]; then
  for plugin in "$ROOT"/plugins/*/; do
    name="$(basename "$plugin")"
    skills="$(find "$plugin/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | tr '\n' ' ')"
    echo "$name: $skills"
  done
  exit 0
fi

[ -n "$PLUGINS" ] || die "name at least one plugin (or all); --list shows them"
if [ "$PLUGINS" = " all" ]; then
  PLUGINS=""
  for plugin in "$ROOT"/plugins/*/; do PLUGINS="$PLUGINS $(basename "$plugin")"; done
fi

mkdir -p "$DEST"
for name in $PLUGINS; do
  case "$name" in *[!a-z0-9-]*|"") die "invalid plugin name: $name" ;; esac
  [ -d "$ROOT/plugins/$name/skills" ] || die "no plugin named $name (--list shows them)"
  for skill in "$ROOT/plugins/$name/skills"/*/; do
    skill="${skill%/}"
    skill_name="$(basename "$skill")"
    [ -f "$skill/SKILL.md" ] || continue
    rm -rf "${DEST:?}/$skill_name"
    cp -R "$skill" "$DEST/$skill_name"
    echo "✔ $name → $DEST/$skill_name"
  done
done
