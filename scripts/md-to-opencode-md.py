#!/usr/bin/env python3
"""Convert canonical agent Markdown to OpenCode agent Markdown."""
from pathlib import Path
import re
import sys


TOOL_MAP = {
    "Read": "read",
    "Write": "write",
    "Edit": "edit",
    "Grep": "grep",
    "Glob": "glob",
    "Bash": "bash",
    "WebFetch": "webfetch",
    "WebSearch": "websearch",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found")
    raw, body = match.group(1), match.group(2).strip()
    frontmatter = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter, body


def map_tools(tools_csv: str) -> dict[str, bool]:
    tools = {"read": False, "write": False, "edit": False, "bash": False}
    for raw_tool in tools_csv.split(","):
        tool = TOOL_MAP.get(raw_tool.strip())
        if tool:
            tools[tool] = True
    return tools


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def convert(md_path: Path, output_dir: Path) -> Path:
    frontmatter, body = parse_frontmatter(md_path.read_text())
    name = frontmatter["name"]
    description = frontmatter["description"]
    tools = map_tools(frontmatter.get("tools", "Read, Grep, Glob"))

    lines = [
        "---",
        f"description: {yaml_quote(description)}",
        "mode: subagent",
        "tools:",
    ]
    lines.extend(f"  {name}: {str(enabled).lower()}" for name, enabled in tools.items())
    lines.extend(["---", "", body, ""])
    output = output_dir / f"{name}.md"
    output.write_text("\n".join(lines))
    return output


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: md-to-opencode-md.py <agents_md_dir> <output_dir>", file=sys.stderr)
        sys.exit(2)
    source_dir, output_dir = map(Path, sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_dir.glob("*.md")):
        print(f"✓ {source.name} → {convert(source, output_dir).name}")


if __name__ == "__main__":
    main()
