"""Clean raw output.md files: remove # headers, type prefixes, number prefixes."""

import re
import sys
from pathlib import Path

DATA_DIR = Path("data")

# Same regex as db.py
_ANNOTATION_RE = re.compile(
    r"<!-- QUESTION: (.*?) -->\s*\n(.*?)\s*\n\s*<!-- QUESTION END -->", re.DOTALL
)
_ANSWER_RE = re.compile(r"\s*<!-- ANSWER -->\s*")
_EXPLANATION_RE = re.compile(r"\s*<!-- EXPLANATION -->\s*")


def clean_line(line: str) -> str:
    """Clean a single line of question content."""
    s = line.rstrip()

    # Skip standalone section headers: ## 二、证明 (nothing follows)
    if re.match(r"^#+\s*[一二三四五六七八九十]+、\S*\s*$", s):
        return ""

    # Remove ## prefix
    s = re.sub(r"^#+\s*", "", s)

    # Strip section header: "一、简答 将下列..." → "将下列..."
    # Strip leading top-level number prefix: 1. 2. 3. (not (1) / （1）)
    s = re.sub(r"^\d+\s*[.、）\)]\s*", "", s, count=1)

    return s


def clean_block_content(body: str) -> str:
    """Clean the content section of one annotation block, preserving answer/explanation."""
    # Split into content / answer / explanation
    ans_it = list(_ANSWER_RE.finditer(body))
    expl_it = list(_EXPLANATION_RE.finditer(body))

    if not ans_it and not expl_it:
        # No answer/explanation markers — entire body is content
        cleaned_lines = [clean_line(l) for l in body.split("\n")]
        cleaned_lines = [l for l in cleaned_lines if l]  # drop empty
        return ("\n\n" if "\n\n" in body else "\n").join(cleaned_lines)

    # Has answer/explanation — split at first marker
    first_marker = min(
        (m.start() for m in ans_it + expl_it),
        default=len(body),
    )
    content_part = body[:first_marker].strip()
    rest = body[first_marker:]

    # Clean content lines
    content_lines = [clean_line(l) for l in content_part.split("\n")]
    content_lines = [l for l in content_lines if l]
    cleaned_content = "\n".join(content_lines) if content_lines else ""

    return cleaned_content + ("\n" if cleaned_content else "") + rest


def process_file(path: Path) -> bool:
    """Clean one output.md file. Returns True if changes were made."""
    original = path.read_text("utf-8")
    changed = False

    def replace_block(m: re.Match) -> str:
        nonlocal changed
        header = m.group(1)
        body = m.group(2)
        cleaned = clean_block_content(body)
        if cleaned != body:
            changed = True
        return f"<!-- QUESTION: {header} -->\n\n{cleaned}\n\n<!-- QUESTION END -->"

    result = _ANNOTATION_RE.sub(replace_block, original)
    if changed:
        path.write_text(result, encoding="utf-8")
    return changed


def main():
    raw_base = DATA_DIR / "离散数学" / "raw"
    if not raw_base.exists():
        print(f"Directory not found: {raw_base}")
        return

    md_files = sorted(raw_base.rglob("output.md"))
    if not md_files:
        print("No output.md files found")
        return

    for md in md_files:
        try:
            ok = process_file(md)
            print(f"{'MODIFIED' if ok else 'SKIPPED'}: {md}")
        except Exception as e:
            print(f"ERROR: {md}: {e}", file=sys.stderr)

    print("Done.")


if __name__ == "__main__":
    main()
