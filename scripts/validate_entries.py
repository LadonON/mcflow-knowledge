"""Knowledge-base entries: frontmatter parsing, validation and version matching.

Standard library only, so the shared knowledge-base repo can run a byte-for-byte copy of this file
in its CI (`scripts/validate_entries.py`) without installing mcflow:

    python scripts/validate_entries.py entries/
"""

import contextlib
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED = ("title", "minecraft_versions", "paper_api_version", "verified_by", "sources", "date")
OPTIONAL = ("pack_format",)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SKIPPED_NAMES = {"README.md"}


class FrontmatterError(ValueError):
    pass


@dataclass
class Entry:
    path: Path
    fields: dict[str, object]
    body: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def title(self) -> str:
        value = self.fields.get("title")
        return value if isinstance(value, str) else self.path.stem

    @property
    def minecraft_versions(self) -> list[str]:
        value = self.fields.get("minecraft_versions")
        return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []

    @property
    def pack_format(self) -> int | None:
        value = self.fields.get("pack_format")
        return value if isinstance(value, int) else None


@dataclass(frozen=True)
class Match:
    applies: bool
    reason: str


def _version_key(text: str) -> tuple[int, ...] | None:
    parts = text.strip().split(".")
    return tuple(int(p) for p in parts) if all(p.isdigit() for p in parts) else None


# --- frontmatter (the small YAML subset entries use) -------------------------------------------


def _strip_comment(line: str) -> str:
    quote, escaped = None, False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
        elif quote == '"' and ch == "\\":
            escaped = True
        elif quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def _scalar(text: str) -> object:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", text[1:-1])
    if len(text) >= 2 and text[0] == text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if text[:1] in "\"'":
        raise FrontmatterError(f"unterminated quote: {text}")
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _inline_list(text: str) -> list[object]:
    inner = text.strip()[1:-1]
    items, current, quote = [], "", None
    for ch in inner:
        if quote:
            current += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            current += ch
        elif ch == ",":
            items.append(current)
            current = ""
        else:
            current += ch
    if quote:
        raise FrontmatterError(f"unterminated quote in list: {text}")
    if current.strip() or items:
        items.append(current)
    return [_scalar(i) for i in items if i.strip()]


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Split `---` frontmatter from the body. Raises FrontmatterError on anything malformed."""
    text = text.removeprefix("﻿").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise FrontmatterError("the file must start with a --- frontmatter block")
    end = text.find("\n---", 3)
    if end == -1 or text[end + 4 : end + 5] not in ("\n", ""):
        raise FrontmatterError("the frontmatter block is never closed with ---")
    block, body = text[4:end], text[end + 5 :]

    fields: dict[str, object] = {}
    open_list: list[object] | None = None
    for number, raw in enumerate(block.split("\n"), start=2):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        item = re.fullmatch(r"\s+-\s*(.*)", line) or re.fullmatch(r"-\s+(.*)", line)
        if item:
            if open_list is None:
                raise FrontmatterError(f"line {number}: list item without a key above it")
            open_list.append(_scalar(item.group(1)))
            continue
        pair = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):(?:\s+(.*))?", line)
        if not pair:
            raise FrontmatterError(f"line {number}: expected `key: value`, got {raw.strip()!r}")
        key, value = pair.group(1), (pair.group(2) or "").strip()
        if key in fields:
            raise FrontmatterError(f"line {number}: {key} appears twice")
        open_list = None
        if not value:
            open_list = []
            fields[key] = open_list
        elif value.startswith("["):
            if not value.endswith("]"):
                raise FrontmatterError(f"line {number}: list for {key} isn't closed with ]")
            fields[key] = _inline_list(value)
        else:
            fields[key] = _scalar(value)
    return fields, body


# --- validation --------------------------------------------------------------------------------


def _non_empty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_fields(fields: dict[str, object], body: str, today: dt.date) -> tuple[list, list]:
    errors: list[str] = []
    warnings: list[str] = []
    for key in REQUIRED:
        if key not in fields or fields[key] in ("", []):
            errors.append(f"{key} is missing")
    for key in fields:
        if key not in REQUIRED and key not in OPTIONAL:
            warnings.append(f"unknown field {key} (it's kept, but nothing reads it)")

    if "title" in fields and not _non_empty_str(fields["title"]):
        errors.append("title must be text")

    versions = fields.get("minecraft_versions")
    if versions not in (None, "", []):
        if not isinstance(versions, list):
            errors.append('minecraft_versions must be a list, e.g. ["1.21.11"]')
        else:
            for v in versions:
                if not isinstance(v, str) or _version_key(v) is None:
                    errors.append(
                        f'minecraft_versions: {v!r} isn\'t a release version; quote it, e.g. "1.21"'
                    )
            if len(set(map(str, versions))) != len(versions):
                errors.append("minecraft_versions lists a version twice")

    api = fields.get("paper_api_version")
    if api not in (None, "") and (not isinstance(api, str) or _version_key(api) is None):
        errors.append(f'paper_api_version {api!r} must be a quoted version, e.g. "1.21"')

    if "pack_format" in fields and (
        not isinstance(fields["pack_format"], int) or fields["pack_format"] < 1
    ):
        errors.append("pack_format must be a whole number (leave it out if packs aren't involved)")

    verified = fields.get("verified_by")
    if verified not in (None, "", []) and not (
        _non_empty_str(verified)
        or (isinstance(verified, list) and all(_non_empty_str(v) for v in verified))
    ):
        errors.append("verified_by must name the test, gate run or screenshot that proved it")

    sources = fields.get("sources")
    if sources not in (None, "", []) and not (
        isinstance(sources, list) and all(_non_empty_str(s) for s in sources)
    ):
        errors.append("sources must be a list of URLs or jar/class references")

    date = fields.get("date")
    if date not in (None, ""):
        parsed = None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(date)):
            with contextlib.suppress(ValueError):
                parsed = dt.date.fromisoformat(str(date))
        if parsed is None:
            errors.append(f"date {date!r} must be YYYY-MM-DD")
        elif parsed > today + dt.timedelta(days=1):
            errors.append(f"date {date} is in the future")

    if not body.strip():
        errors.append("the entry has no body: say how to do it and what was proven")
    return errors, warnings


def load(path: Path, today: dt.date | None = None) -> Entry:
    today = today or dt.date.today()
    try:
        fields, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    except (FrontmatterError, UnicodeDecodeError) as e:
        return Entry(path, {}, "", errors=[str(e)])
    errors, warnings = validate_fields(fields, body, today)
    if not NAME_RE.match(path.name):
        errors.append("file name must be lowercase words joined by hyphens, e.g. font-glyph-ui.md")
    return Entry(path, fields, body, errors, warnings)


def entry_files(folder: Path) -> list[Path]:
    """Entry files directly in `folder` (the README and non-Markdown files aren't entries)."""
    if not folder.is_dir():
        return []
    return sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix == ".md" and p.name not in SKIPPED_NAMES
    )


# --- version matching --------------------------------------------------------------------------


def applies(entry: Entry, minecraft_version: str, pack_format: int | None = None) -> Match:
    """An entry applies only to versions it was proven on, and only to the same pack format.

    No ranges or "probably works on newer": an entry for another version is a lead for research.
    """
    if not entry.ok:
        return Match(False, "the entry is invalid")
    target = _version_key(minecraft_version)
    proven = {_version_key(v) for v in entry.minecraft_versions}
    if target not in proven:
        listed = ", ".join(entry.minecraft_versions)
        return Match(False, f"proven on {listed}, not {minecraft_version}")
    if (
        pack_format is not None
        and entry.pack_format is not None
        and entry.pack_format != pack_format
    ):
        return Match(False, f"pack format {entry.pack_format}, but this project uses {pack_format}")
    return Match(True, f"proven on {minecraft_version}")


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv] or [Path("entries")]
    files: list[Path] = []
    for t in targets:
        files.extend(entry_files(t) if t.is_dir() else [t])
    if not files:
        print("No entries found.")
        return 0
    failed = 0
    for path in files:
        entry = load(path)
        for w in entry.warnings:
            print(f"{path}: warning: {w}")
        for e in entry.errors:
            print(f"{path}: error: {e}")
        failed += not entry.ok
    print(f"{len(files)} entries checked, {failed} invalid.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
