#!/bin/bash
# usage: verify.sh <label>   -> validation + metrics
cd "$(dirname "$0")/../.."
R=/Users/yaroslav/.claude/plugins/cache/lore-framework/lr/1.47.0/scripts/lr-core
python3 $R lore-map --agent-dir "$PWD" --view detailed > /tmp/m_$$.yaml
echo "validation:"; sed -n '/^validation:/,$p' /tmp/m_$$.yaml | head -20
rm /tmp/m_$$.yaml
python3 workdir/grooming-exercise/measure.py "$1"
