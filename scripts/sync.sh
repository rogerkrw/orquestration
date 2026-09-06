#!/usr/bin/env bash
# Sync canonical agents and skills from orquestration/ to ~/.{claude,codex,gemini}/
# (Antigravity CLI/IDE are covered via ~/.gemini/config + ~/.gemini/antigravity-cli)
# Idempotent — safe to run multiple times.
#
# CANONICAL SOURCE LAYOUT (this repo):
#   agents/*.md       <- 9 agents, canonical Markdown (PascalCase tools, alias model)
#   skills/<name>/    <- 27 skills, expanded folders (SKILL.md + references/)
#
# Per-CLI agent variants are GENERATED into .build/ at sync time.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_MD="$ROOT/agents"
SKILLS="$ROOT/skills"
BUILD="$ROOT/.build"            # generated per-CLI agent variants (gitignorable)
AGENTS_TOML="$BUILD/agents-codex"
AGENTS_GEMINI="$BUILD/agents-gemini"
AGENTS_OPENCODE="$BUILD/agents-opencode"
AGENTS_ANTIGRAVITY="$BUILD/agents-antigravity"
ANTIGRAVITY_PLUGIN="$BUILD/plugin-antigravity/orquestration"

# ---------------------------------------------------------------------------
# 1. Regenerate per-CLI agent variants from canonical .md
#    - Codex needs TOML (no `tools` allowlist; sandbox_mode derived)
#    - Gemini needs .md with YAML array tools + snake_case names + Gemini model IDs
# ---------------------------------------------------------------------------
# .build/ is regenerated from scratch: the generators only write, never delete,
# so a renamed/retired agent would linger there and get copied to every CLI.
rm -rf "$AGENTS_TOML" "$AGENTS_GEMINI" "$AGENTS_OPENCODE" "$AGENTS_ANTIGRAVITY" "$ANTIGRAVITY_PLUGIN"
mkdir -p "$AGENTS_TOML" "$AGENTS_GEMINI" "$AGENTS_OPENCODE" "$AGENTS_ANTIGRAVITY"
python3 "$ROOT/scripts/md-to-codex-toml.py"  "$AGENTS_MD" "$AGENTS_TOML"   >/dev/null
python3 "$ROOT/scripts/md-to-gemini-md.py"   "$AGENTS_MD" "$AGENTS_GEMINI" >/dev/null
python3 "$ROOT/scripts/md-to-opencode-md.py" "$AGENTS_MD" "$AGENTS_OPENCODE" >/dev/null
python3 "$ROOT/scripts/md-to-antigravity-md.py" "$AGENTS_MD" "$AGENTS_ANTIGRAVITY" >/dev/null

# Antigravity plugins are the portable bundle for agents, skills and references.
mkdir -p "$ANTIGRAVITY_PLUGIN/agents" "$ANTIGRAVITY_PLUGIN/skills"
cp "$ROOT/antigravity/plugin.json" "$ANTIGRAVITY_PLUGIN/plugin.json"
cp "$AGENTS_ANTIGRAVITY"/*.md "$ANTIGRAVITY_PLUGIN/agents/"
for skill in "$SKILLS"/*/; do
  [ -d "$skill" ] || continue
  rsync -a --delete "$skill" "$ANTIGRAVITY_PLUGIN/skills/$(basename "$skill")/"
done

# ---------------------------------------------------------------------------
# 2. Sync agents (clean stale files first to avoid leftovers from previous runs)
# ---------------------------------------------------------------------------
mkdir -p ~/.claude/agents ~/.codex/agents ~/.gemini/agents
rm -f ~/.claude/agents/*.md ~/.codex/agents/*.toml ~/.gemini/agents/*.md
cp "$AGENTS_MD"/*.md       ~/.claude/agents/
cp "$AGENTS_TOML"/*.toml   ~/.codex/agents/
cp "$AGENTS_GEMINI"/*.md   ~/.gemini/agents/

# OpenCode uses its own global Markdown locations and inherits the active model
# from the primary agent, so the same generated agents work with Zen and Go.
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
rm -f ~/.config/opencode/agents/*.md
cp "$AGENTS_OPENCODE"/*.md ~/.config/opencode/agents/

# Antigravity CLI/IDE: read agents from ~/.gemini/antigravity-cli/agents (Gemini .md format)
mkdir -p ~/.gemini/antigravity-cli/agents
rm -f ~/.gemini/antigravity-cli/agents/*.md
cp "$AGENTS_GEMINI"/*.md   ~/.gemini/antigravity-cli/agents/

# Current Antigravity CLI global agent location. Keep the legacy shared path
# above for Gemini/older installations; the plugin is the preferred bundle.
mkdir -p ~/.gemini/config/agents ~/.gemini/antigravity-cli/plugins
rm -f ~/.gemini/config/agents/*.md
cp "$AGENTS_ANTIGRAVITY"/*.md ~/.gemini/config/agents/
if command -v agy >/dev/null 2>&1; then
  # Use the official installer so the plugin is registered, not merely staged.
  agy plugin install "$ANTIGRAVITY_PLUGIN" >/dev/null
else
  # Keep the package available for a later `agy plugin install` on new machines.
  rsync -a --delete "$ANTIGRAVITY_PLUGIN/" ~/.gemini/antigravity-cli/plugins/orquestration/
fi

# ---------------------------------------------------------------------------
# 3. Sync skills (rsync --delete keeps each skill folder clean)
# ---------------------------------------------------------------------------
for tool_dir in ~/.claude/skills ~/.codex/skills ~/.gemini/skills ~/.config/opencode/skills; do
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
echo "✓ Synced to OpenCode, Claude, Codex, Gemini and Antigravity CLI/IDE"
echo ""
echo "Agents (~/.claude/agents/):"
/bin/ls -1 ~/.claude/agents/ | sed 's/^/  /'
echo ""
echo "Skills (~/.claude/skills/):"
/bin/ls -1 ~/.claude/skills/ | sed 's/^/  /'
