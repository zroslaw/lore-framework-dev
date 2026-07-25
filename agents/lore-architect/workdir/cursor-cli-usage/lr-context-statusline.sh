#!/usr/bin/env bash
# Cursor CLI statusline hook: context % bar + JSON snapshot for polling.
# Wire via ~/.cursor/cli-config.json statusLine.command -> this script.

set -euo pipefail

payload=$(cat)
cache="${LR_CONTEXT_USAGE_CACHE:-${HOME}/.cursor/context-usage.json}"

model=$(echo "$payload" | jq -r '.model.display_name // .model.id // "unknown"')
pct=$(echo "$payload" | jq -r '.context_window.used_percentage // empty')
input_tokens=$(echo "$payload" | jq -r '.context_window.total_input_tokens // empty')
window_size=$(echo "$payload" | jq -r '.context_window.context_window_size // empty')
session_name=$(echo "$payload" | jq -r '.session_name // empty')

jq -n \
  --argjson raw "$payload" \
  --arg checked_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  '{
    checked_at: $checked_at,
    session_id: ($raw.session_id // null),
    session_name: ($raw.session_name // null),
    model: ($raw.model.display_name // $raw.model.id // null),
    context: {
      used_percent: ($raw.context_window.used_percentage // null),
      remaining_percent: ($raw.context_window.remaining_percentage // null),
      input_tokens: ($raw.context_window.total_input_tokens // null),
      output_tokens: ($raw.context_window.total_output_tokens // null),
      window_size: ($raw.context_window.context_window_size // null),
      current_usage: ($raw.context_window.current_usage // null)
    }
  }' >"$cache"

if [[ -z "$pct" ]]; then
  printf '\033[90m%s  ctx …\033[0m' "$model"
  exit 0
fi

pct_int=${pct%.*}
bar_width=10
filled=$((pct_int * bar_width / 100))
empty=$((bar_width - filled))
bar=""
if (( filled > 0 )); then
  printf -v fill "%${filled}s" ''
  bar="${fill// /▓}"
fi
if (( empty > 0 )); then
  printf -v pad "%${empty}s" ''
  bar="${bar}${pad// /░}"
fi

color='\033[32m'
if (( pct_int >= 90 )); then color='\033[31m'
elif (( pct_int >= 70 )); then color='\033[33m'
fi

token_bits=""
if [[ -n "$input_tokens" && "$input_tokens" != "null" && -n "$window_size" && "$window_size" != "null" ]]; then
  token_bits="  ${input_tokens}/${window_size} tok"
fi

name_bit="$model"
if [[ -n "$session_name" && "$session_name" != "null" ]]; then
  name_bit="$session_name"
fi

printf '%b%s%b  %s  ctx %s%%%s' "$color" "$name_bit" '\033[0m' "$bar" "$pct_int" "$token_bits"
