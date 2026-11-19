#!/bin/sh
# Runs every browser test against index.html. Needs: pip install playwright && python3 -m playwright install chromium
cd "$(dirname "$0")" && for t in test_*.py; do echo "== $t"; python3 "$t" || exit 1; done
