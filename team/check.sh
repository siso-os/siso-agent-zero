#!/bin/sh
# Existing repository offline verification.
set -eu
export PYTHONDONTWRITEBYTECODE=1
# macOS system Python has the existing PyYAML prerequisite.
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  PATH=/usr/bin:$PATH
  export PATH
fi
python3 -c "import yaml"
bash tools/test-brief-routing.sh
bash tools/test-worktree-routing.sh
