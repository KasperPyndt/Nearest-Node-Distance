#!/bin/zsh
set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1
REPO_DIR="${0:A:h:h}"
GLYPHS_RUNNER="${GLYPHS_RUNNER:-glyphs}"
GLYPHS_APP="${GLYPHS_APP:-/Applications/Glyphs 4.app}"

"$GLYPHS_RUNNER" run -a "$GLYPHS_APP" --plugins '' "$REPO_DIR/tests/native_check.py"
"$GLYPHS_RUNNER" run -a "$GLYPHS_APP" --plugins "$REPO_DIR/Nearest Node Distance.glyphsReporter" "$REPO_DIR/tests/reporter_check.py"
