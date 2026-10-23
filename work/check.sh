#!/bin/sh
# Existing repository offline verification.
set -eu
export PYTHONDONTWRITEBYTECODE=1
npm test
npm run check
npm pack --dry-run
