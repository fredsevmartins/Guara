"""Check local Markdown and HTML image targets without making network requests."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)')
HTML_SOURCE = re.compile(r'<img\b[^>]*\bsrc=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)


def check(root=ROOT):
    errors = []
    documents = sorted(root.glob("*.md")) + sorted((root / "docs").rglob("*.md"))
    for document in documents:
        text = document.read_text(encoding="utf-8")
        targets = [(m.start(), m.group(1).strip("<>")) for m in MARKDOWN_LINK.finditer(text)]
        targets += [(m.start(), m.group(1)) for m in HTML_SOURCE.finditer(text)]
        for position, target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (document.parent / unquote(parsed.path)).resolve()
            line = text.count("\n", 0, position) + 1
            if not path.is_relative_to(root.resolve()):
                errors.append(f"{document.relative_to(root)}:{line}: target leaves project: {target}")
            elif not path.exists():
                errors.append(f"{document.relative_to(root)}:{line}: missing target: {target}")
    return documents, errors


if __name__ == "__main__":
    documents, errors = check()
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"Local file links and image targets: PASS ({len(documents)} documents; no URL/anchor checks)")
