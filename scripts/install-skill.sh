#!/usr/bin/env bash
# Copy one Guzli skill into a host skills root.
# Usage: ./scripts/install-skill.sh <skill-name> <destination-skills-root>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:?skill name e.g. guzli-mcp-core}"
DEST="${2:?destination skills root e.g. ~/.claude/skills}"
SRC="$ROOT/skills/$NAME"
test -f "$SRC/SKILL.md" || { echo "missing $SRC/SKILL.md" >&2; exit 1; }
mkdir -p "$DEST"
rm -rf "$DEST/$NAME"
cp -R "$SRC" "$DEST/$NAME"
echo "Installed $NAME -> $DEST/$NAME"
