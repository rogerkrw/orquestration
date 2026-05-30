#!/usr/bin/env python3
"""
Convert Claude Code agent .md (frontmatter w/ CSV `tools` field, PascalCase tool
names, alias `model`) into Gemini CLI-compatible agent .md.

Gemini CLI (verified via geminicli.com/docs/core/subagents, May 2026) requires:
  - `tools` as a YAML array, not a CSV string
  - snake_case tool names: read_file, write_file, grep_search, run_shell_command,
    list_directory, web_fetch, web_search (vs Claude's Read/Write/Grep/Bash/Glob/WebFetch/WebSearch)
  - `model` is a Gemini model ID, not an alias

Tool name mapping (Claude → Gemini):
  Read       -> read_file
  Write      -> write_file
  Edit       -> write_file       (Gemini has no separate Edit; folded into write_file)
  Grep       -> grep_search
  Glob       -> glob             (verified in some agent examples; falls back as-is)
  Bash       -> run_shell_command
  WebFetch   -> web_fetch
  WebSearch  -> web_search

Model mapping (Claude alias → Gemini model, per TPM directive May 2026):
  opus    -> gemini-3.1-pro-preview   (highest capability for supervision/challenger roles)
  sonnet  -> gemini-3.5-flash         (mid-tier, fast, default executor)
  haiku   -> gemini-3.1-flash-lite    (cheapest, low-latency; GA — preview shut down 2026-07-09)

Adjust MODEL_MAP if Google changes model IDs.
"""
from pathlib import Path
import re
import sys

TOOL_MAP = {
    "Read": "read_file",
    "Write": "write_file",
    "Edit": "edit",
    "Grep": "grep_search",
    "Glob": "glob",
    "Bash": "run_shell_command",
    "WebFetch": "web_fetch",
    "WebSearch": "google_web_search",
}

MODEL_MAP = {
    "opus": "gemini-3.1-pro-preview",
    "sonnet": "gemini-3.5-flash",
    "haiku": "gemini-3.1-flash-lite",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("No YAML frontmatter found")
    raw_fm, body = m.group(1), m.group(2).strip()
    fm = {}
    for line in raw_fm.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def map_tools(csv: str) -> list[str]:
    raw = [t.strip() for t in csv.split(",")]
    seen = set()
    out = []
    for t in raw:
        mapped = TOOL_MAP.get(t, t)
        if mapped not in seen:
            out.append(mapped)
            seen.add(mapped)
    return out


def convert(md_path: Path, out_dir: Path) -> Path:
    text = md_path.read_text()
    fm, body = parse_frontmatter(text)

    name = fm["name"]
    description = fm["description"]
    model_alias = fm.get("model", "sonnet")
    model = MODEL_MAP.get(model_alias, model_alias)
    tools = map_tools(fm.get("tools", "Read, Grep, Glob"))

    # YAML double-quoted strings need internal " escaped as \"
    description_yaml = description.replace("\\", "\\\\").replace('"', '\\"')

    lines = [
        "---",
        f"name: {name}",
        f'description: "{description_yaml}"',
        f"model: {model}",
        "tools:",
    ]
    for t in tools:
        lines.append(f"  - {t}")
    lines.extend(["---", "", body, ""])

    out_path = out_dir / f"{name}.md"
    out_path.write_text("\n".join(lines))
    return out_path


def main():
    if len(sys.argv) != 3:
        print("Usage: md-to-gemini-md.py <agents_md_dir> <output_dir>", file=sys.stderr)
        sys.exit(2)
    in_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for md in sorted(in_dir.glob("*.md")):
        out = convert(md, out_dir)
        print(f"✓ {md.name} → {out.name}")


if __name__ == "__main__":
    main()
