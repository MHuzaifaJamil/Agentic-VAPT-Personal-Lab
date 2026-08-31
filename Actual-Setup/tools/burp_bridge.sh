#!/usr/bin/env bash
# cc-bridge REST API wrapper for Claude Code
# Usage: burp_bridge.sh <endpoint> [curl-args...]
# Examples:
#   burp_bridge.sh /health
#   burp_bridge.sh /history
#   burp_bridge.sh /history/0
#   burp_bridge.sh /send -X POST -d '{"url":"https://target.com/api","method":"GET"}'

BURP_URL="${BURP_API_URL:-http://127.0.0.1:1337}"
TOKEN_FILE="${HOME}/.cc-bridge-token"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "ERROR: ~/.cc-bridge-token not found. Load cc-bridge extension in Burp first." >&2
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")
ENDPOINT="${1:-/health}"
shift 2>/dev/null || true

curl -s -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     "$BURP_URL$ENDPOINT" "$@"
