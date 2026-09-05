#!/usr/bin/env bash
# Sync canonical agents and skills from orquestration/ to ~/.{claude,codex,gemini}/
# (Antigravity CLI/IDE are covered via ~/.gemini shared paths + ~/.gemini/antigravity-cli/agents)
# Idempotent — safe to run multiple times.
#
# CANONICAL SOURCE LAYOUT (this repo):
#   agents/*.md       <- 7 agents, Claude .md format (PascalCase tools, alias model)
#   skills/<name>/    <- 24 skills, expanded folders (SKILL.md + references/)
#
# Per-CLI agent variants (Codex .toml, Gemini .md) are GENERATED into .build/ at sync time.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_MD="$ROOT/agents"
SKILLS="$ROOT/skills"
BUILD="$ROOT/.build"            # generated per-CLI agent variants (gitignorable)
AGENTS_TOML="$BUILD/agents-codex"
AGENTS_GEMINI="$BUILD/agents-gemini"

# ---------------------------------------------------------------------------
# 1. Regenerate per-CLI agent variants from canonical .md
#    - Codex needs TOML (no `tools` allowlist; sandbox_mode derived)
#    - Gemini needs .md with YAML array tools + snake_case names + Gemini model IDs
# ---------------------------------------------------------------------------
# .build/ is regenerated from scratch: the generators only write, never delete,
# so a renamed/retired agent would linger there and get copied to every CLI.
rm -rf "$AGENTS_TOML" "$AGENTS_GEMINI"
mkdir -p "$AGENTS_TOML" "$AGENTS_GEMINI"
python3 "$ROOT/scripts/md-to-codex-toml.py"  "$AGENTS_MD" "$AGENTS_TOML"   >/dev/null
python3 "$ROOT/scripts/md-to-gemini-md.py"   "$AGENTS_MD" "$AGENTS_GEMINI" >/dev/null

# ---------------------------------------------------------------------------
# 2. Sync agents (clean stale files first to avoid leftovers from previous runs)
# ---------------------------------------------------------------------------
mkdir -p ~/.claude/agents ~/.codex/agents ~/.gemini/agents
rm -f ~/.claude/agents/*.md ~/.codex/agents/*.toml ~/.gemini/agents/*.md
cp "$AGENTS_MD"/*.md       ~/.claude/agents/
cp "$AGENTS_TOML"/*.toml   ~/.codex/agents/
cp "$AGENTS_GEMINI"/*.md   ~/.gemini/agents/

# Antigravity CLI/IDE: read agents from ~/.gemini/antigravity-cli/agents (Gemini .md format)
mkdir -p ~/.gemini/antigravity-cli/agents
rm -f ~/.gemini/antigravity-cli/agents/*.md
cp "$AGENTS_GEMINI"/*.md   ~/.gemini/antigravity-cli/agents/

# ---------------------------------------------------------------------------
# 3. Sync skills (rsync --delete keeps each skill folder clean)
# ---------------------------------------------------------------------------
for tool_dir in ~/.claude/skills ~/.codex/skills ~/.gemini/skills; do
  mkdir -p "$tool_dir"
  for skill in "$SKILLS"/*/; do
    [ -d "$skill" ] || continue
    rsync -a --delete "$skill" "$tool_dir/$(basename "$skill")/"
  done
  # Remove skills that no longer exist in the canonical source (renamed/retired).
  # Without this, a renamed skill lingers in the destination as an orphan copy.
  for installed in "$tool_dir"/*/; do
    [ -d "$installed" ] || continue
    name="$(basename "$installed")"
    [ -d "$SKILLS/$name" ] || { echo "  - removing stale skill: $name ($tool_dir)"; rm -rf "$installed"; }
  done
done

# ---------------------------------------------------------------------------
# 4. Mirror GEMINI.md -> AGENTS.md
#    Antigravity desktop prefers AGENTS.md; Gemini CLI and agy read GEMINI.md.
# ---------------------------------------------------------------------------
if [ -f ~/.gemini/GEMINI.md ]; then
  cp ~/.gemini/GEMINI.md ~/.gemini/AGENTS.md
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
echo "✓ Synced to ~/.claude, ~/.codex, ~/.gemini (+ Antigravity CLI/IDE via ~/.gemini)"
echo ""
echo "Agents (~/.claude/agents/):"
/bin/ls -1 ~/.claude/agents/ | sed 's/^/  /'
echo ""
echo "Skills (~/.claude/skills/):"
/bin/ls -1 ~/.claude/skills/ | sed 's/^/  /'
