#!/bin/bash
# =============================================================================
# Plugin Bootstrap — re-declares Claude Code plugins/marketplaces this project
# depends on, every session start.
#
# WHY THIS EXISTS: like tool installs under $HOME (see bootstrap_arsenal.sh),
# the Claude Code plugin cache (~/.claude/plugins/) does not survive a
# container/sandbox reset — only the git repo does. Both `claude plugin
# marketplace add` and `claude plugin install` are cleanly idempotent (exit 0,
# no prompts, no re-download when already present), so re-running them every
# session costs nothing when the cache is warm and fully re-materializes it
# when the cache is cold. No settings.json state is relied on — this script
# is self-sufficient.
#
# KNOWN RACE CONDITION (confirmed by testing): immediately after a fresh
# `marketplace add` (cold cache), the very next `plugin install` can fail
# with "cache-miss" — the marketplace catalog isn't queryable yet. It always
# succeeds on retry a couple seconds later. The install loop below retries.
#
# Usage:
#   bash tools/bootstrap_plugins.sh
# =============================================================================

set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
ok()  { echo -e "${GREEN}[+]${NC} $1"; }
err() { echo -e "${RED}[-]${NC} $1"; }

if ! command -v claude >/dev/null 2>&1; then
  err "claude CLI not found on PATH — skipping plugin bootstrap"
  exit 0
fi

# name|source
PLUGIN_MARKETPLACES=(
  "anthropic-cybersecurity-skills|mukul975/Anthropic-Cybersecurity-Skills"
)

# plugin@marketplace
PLUGINS=(
  "cybersecurity-skills@anthropic-cybersecurity-skills"
)

echo "--- Plugin marketplaces ---"
for entry in "${PLUGIN_MARKETPLACES[@]}"; do
  name="${entry%%|*}"
  source="${entry##*|}"
  if claude plugin marketplace add "$source" >/tmp/bootstrap_plugins_err.log 2>&1; then
    ok "marketplace: $name"
  else
    err "marketplace: $name — $(tail -1 /tmp/bootstrap_plugins_err.log)"
  fi
done

echo
echo "--- Plugins ---"
for plugin in "${PLUGINS[@]}"; do
  installed=false
  for attempt in 1 2 3 4 5; do
    if claude plugin install "$plugin" >/tmp/bootstrap_plugins_err.log 2>&1; then
      installed=true
      break
    fi
    sleep 3
  done
  if [ "$installed" = true ]; then
    ok "$plugin"
  else
    err "$plugin — $(tail -1 /tmp/bootstrap_plugins_err.log)"
  fi
done

rm -f /tmp/bootstrap_plugins_err.log
