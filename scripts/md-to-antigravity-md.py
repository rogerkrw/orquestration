#!/usr/bin/env python3
"""Convert canonical agent Markdown to Antigravity CLI agent Markdown."""
from pathlib import Path
import re
import sys


TOOL_MAP = {
    "Read": "view_file",
    "Write": "write_to_file",
    "Edit": "replace_file_content",
    "Grep": "grep_search",
    "Glob": "code_search",
    "Bash": "run_command",
    "WebFetch": "web_fetch",
    "WebSearch": "web_search",
}

MODEL_MAP = {"opus": "pro", "sonnet": "flash"}


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


def map_tools(tools_csv: str) -> list[str]:
    seen = set()
    result = []
    for raw_tool in tools_csv.split(","):
        tool = TOOL_MAP.get(raw_tool.strip())
        if tool and tool not in seen:
            result.append(tool)
            seen.add(tool)
    return result


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def convert(md_path: Path, output_dir: Path) -> Path:
    frontmatter, body = parse_frontmatter(md_path.read_text())
    name = frontmatter["name"]
    description = frontmatter["description"]
    model = MODEL_MAP.get(frontmatter.get("model", "sonnet"), "flash")
    tools = map_tools(frontmatter.get("tools", "Read, Grep, Glob"))

    lines = [
        "---",
        f"name: {name}",
        f"description: {yaml_quote(description)}",
        "mainAgent: false",
        "subagent: true",
        f"model: {model}",
        "commandExecutionPolicy: sandbox",
        "tools:",
    ]
    lines.extend(f"  - {tool}" for tool in tools)
    lines.extend(["---", "", body, ""])
    output = output_dir / f"{name}.md"
    output.write_text("\n".join(lines))
    return output


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: md-to-antigravity-md.py <agents_md_dir> <output_dir>", file=sys.stderr)
        sys.exit(2)
    source_dir, output_dir = map(Path, sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_dir.glob("*.md")):
        print(f"✓ {source.name} → {convert(source, output_dir).name}")


if __name__ == "__main__":
    main()
