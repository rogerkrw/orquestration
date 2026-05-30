#!/usr/bin/env python3
"""
Convert Claude Code / Gemini CLI agent .md files (YAML frontmatter + body)
into Codex CLI .toml agent files.

Codex schema (per OpenAI docs, late 2025):
    name = "..."
    description = "..."
    developer_instructions = '''...'''
    model = "..."                      # optional
    model_reasoning_effort = "..."     # optional: low | medium | high
    sandbox_mode = "..."               # optional: read-only | workspace-write | danger-full-access

Codex has no `tools` allowlist field — tool surface is controlled via sandbox_mode
and via MCP server enabled_tools/disabled_tools at the global config level.
We map the .md `tools` field to sandbox_mode using a heuristic:
    - Read-only set (Read/Grep/Glob, no Write/Edit/Bash) → read-only
    - Includes Write/Edit but no Bash → workspace-write
    - Includes Bash → workspace-write (devsecops Execute mode still requires explicit confirmation in prompt)

Model mapping (Claude alias → Codex model, per TPM directive May 2026):
    opus    → gpt-5.5         (frontier — supervision, problem space, critical reasoning)
    sonnet  → gpt-5.3-codex   (coding specialist — execution work)
    haiku   → gpt-5.3-codex   (same coding model with low reasoning_effort)

TPM directive: ignore gpt-5.4 / gpt-5.4-mini tiers. Only use:
  - gpt-5.5 for supervision (problem space + devsecops incidents)
  - gpt-5.3-codex for trivial / executor tasks (solution space)

Reasoning effort levels (verified, Codex CLI docs):
  minimal | low | medium | high | xhigh
UI label "Altíssimo" maps to `xhigh` (NOT `very-high`).
"""
from pathlib import Path
import re
import sys

MODEL_MAP = {
    "opus": "gpt-5.5",
    "sonnet": "gpt-5.3-codex",
    "haiku": "gpt-5.3-codex",
}

REASONING_MAP = {
    "opus": "high",
    "sonnet": "medium",
    "haiku": "low",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("No YAML frontmatter found")
    raw_fm, body = m.group(1), m.group(2).strip()
    fm = {}
    for line in raw_fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def derive_sandbox(tools_str: str) -> str:
    tools = {t.strip() for t in tools_str.split(",")}
    if {"Write", "Edit"} & tools or "Bash" in tools:
        return "workspace-write"
    return "read-only"


def toml_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def convert(md_path: Path, out_dir: Path) -> Path:
    text = md_path.read_text()
    fm, body = parse_frontmatter(text)

    name = fm["name"]
    description = fm["description"]
    model_alias = fm.get("model", "sonnet")
    model = MODEL_MAP.get(model_alias, model_alias)
    reasoning = REASONING_MAP.get(model_alias, "medium")
    sandbox = derive_sandbox(fm.get("tools", "Read, Grep, Glob"))

    toml_lines = [
        f'name = "{toml_escape(name)}"',
        f'description = "{toml_escape(description)}"',
        f'model = "{model}"',
        f'model_reasoning_effort = "{reasoning}"',
        f'sandbox_mode = "{sandbox}"',
        "",
        'developer_instructions = """',
        body,
        '"""',
        "",
    ]
    out_path = out_dir / f"{name}.toml"
    out_path.write_text("\n".join(toml_lines))
    return out_path


def main():
    if len(sys.argv) != 3:
        print("Usage: md-to-codex-toml.py <agents_md_dir> <output_toml_dir>", file=sys.stderr)
        sys.exit(2)
    in_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for md in sorted(in_dir.glob("*.md")):
        out = convert(md, out_dir)
        written.append(out.name)
        print(f"✓ {md.name} → {out.name}")
    print(f"\nGenerated {len(written)} TOML files in {out_dir}")


if __name__ == "__main__":
    main()
