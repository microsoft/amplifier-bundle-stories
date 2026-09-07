#!/usr/bin/env bash
# Render the delegate agent catalog from a scratch session. No LLM call, $0.
# Usage: render-catalog.sh <out-file>
set -euo pipefail
OUT="${1:?usage: render-catalog.sh <out-file>}"
BUNDLE="${KP79_BUNDLE:-kp79-stories-scratch}"
amplifier tool info delegate -b "$BUNDLE" --format json 2>/dev/null \
  | python3 -c '
import json,sys
raw=sys.stdin.read()
d=json.loads(raw[raw.index("{"):])
sys.stdout.write(d["config_summary"]["description"])
' > "$OUT"
wc -c "$OUT"
