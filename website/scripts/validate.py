"""Validate the generated static site using only the Python standard library.

Run from any directory: python website/scripts/validate.py
Optionally supply another output directory: python scripts/validate.py --dist dist
External links are recorded but are not fetched by this offline check.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


SITE_HOST = "milletszone.com"
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
PURCHASE_ROUTE = re.compile(r"^(?:buy|order|cart|checkout|shop|shopping-cart)(?:[._-]|$)", re.I)
PURCHASE_LABEL = re.compile(
    r"^(?:buy(?:\s+now|\s+online)?|order(?:\s+now|\s+online)?|purchase|"
    r"shop(?:\s+now)?|start\s+shopping|(?:view\s+)?(?:shopping\s+)?cart(?:\s*\(\d+\))?|"
    r"add\s+to\s+(?:cart|bag)|(?:proceed\s+to\s+)?checkout|place\s+(?:an?\s+)?order)$",
    re.I,
)
PLACEHOLDER = re.compile(
    r"\blorem\s+ipsum\b|\b(?:TODO|FIXME)\b|\b(?:insert|replace)\s+(?:text|image|content)\s+here\b|"
    r"\byour\s+(?:text|title)\s+here\b|\btext\s+to\s+be\s+expanded\b|"
    r"\bclick\s+here\s+to\s+add\s+your\s+own\s+text\b|\bimage\s+(?:not\s+found|unavailable)\b|"
    r"\[object\s+Object\]|\bundefined\b|\{\{[^{}]+\}\}",
    re.I,
)


@dataclass
class Reference:
    value: str
    line: int
    attribute: str


@dataclass
class Action:
    tag: str
    line: int
    label: str = ""
    text: list[str] = field(default_factory=list)


class Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: Counter[str] = Counter()
        self.references: list[Reference] = []
        self.canonicals: list[str] = []
        self.actions: list[Action] = []
        self.stack: list[tuple[str, Action | None]] = []
        self.visible_text: list[str] = []
        self.issues: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]):
        attrs = dict(attributes)
        line = self.getpos()[0]
        element_id = attrs.get("id")
        if element_id:
            self.ids[element_id] += 1
        if tag == "a" and attrs.get("name"):
            # Named anchors still occur in archived content; they are valid targets.
            self.ids.setdefault(attrs["name"], 1)
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attrs:
            self.issues.append(f"line {line}: image has no alt attribute")
        for attribute in ("href", "src", "poster"):
            if attribute in attrs:
                self.references.append(Reference(attrs[attribute] or "", line, attribute))
        if attrs.get("srcset"):
            for candidate in attrs["srcset"].split(","):
                source = candidate.strip().split()
                if source and not source[0].startswith("data:"):
                    self.references.append(Reference(source[0], line, "srcset"))
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href") or "")
        action = None
        if tag in {"a", "button"} or (tag == "input" and attrs.get("type", "").lower() in {"submit", "button"}):
            action = Action(tag, line, attrs.get("aria-label") or attrs.get("value") or "")
            self.actions.append(action)
        if tag not in VOID_TAGS:
            self.stack.append((tag, action))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str):
        if any(tag in {"script", "style"} for tag, _ in self.stack):
            return
        self.visible_text.append(data)
        for _, action in self.stack:
            if action is not None:
                action.text.append(data)


def purchase_path(path: str) -> bool:
    return any(PURCHASE_ROUTE.match(part) for part in unquote(path).strip("/").split("/"))


def resolve_reference(dist: Path, page: Path, reference: str) -> tuple[Path | None, str]:
    """Return the local target and fragment, or None for an external resource."""
    parsed = urlsplit(reference)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None, ""
    if parsed.netloc and parsed.hostname not in {SITE_HOST, "www." + SITE_HOST}:
        return None, ""
    raw_path = unquote(parsed.path)
    if not raw_path:
        target = page if not parsed.netloc else dist / "index.html"
    elif raw_path.startswith("/") or parsed.netloc:
        target = dist / raw_path.lstrip("/")
    else:
        target = page.parent / raw_path
    target = target.resolve()
    if not target.is_relative_to(dist):
        raise ValueError("reference escapes the generated site directory")
    if target.is_dir():
        target /= "index.html"
    return target, unquote(parsed.fragment)


def validate(dist: Path) -> int:
    dist = dist.resolve()
    files = sorted(dist.rglob("*.html")) if dist.is_dir() else []
    if not files:
        print(f"FAIL: no generated HTML found in {dist}. Run python build.py first.")
        return 1
    pages: dict[Path, Page] = {}
    failures: list[str] = []
    local_count = 0
    external_count = 0

    def fail(page: Path, message: str):
        failures.append(f"{page.relative_to(dist).as_posix()}: {message}")

    for file in files:
        page = Page(file)
        pages[file] = page
        try:
            page.feed(file.read_text(encoding="utf-8"))
            page.close()
        except (UnicodeError, OSError, ValueError) as error:
            fail(file, f"cannot parse HTML: {error}")
            continue
        if purchase_path(file.relative_to(dist).as_posix()):
            fail(file, "purchase page is excluded from this informational website")
        for issue in page.issues:
            fail(file, issue)
        for value, count in page.ids.items():
            if count > 1:
                fail(file, f"duplicate id {value!r} ({count} occurrences)")
        if page.h1_count != 1:
            fail(file, f"expected exactly one h1, found {page.h1_count}")
        if len(page.canonicals) != 1:
            fail(file, f"expected exactly one canonical URL, found {len(page.canonicals)}")
        else:
            try:
                canonical = urlsplit(page.canonicals[0])
                if canonical.scheme != "https" or canonical.netloc != SITE_HOST or canonical.query or canonical.fragment:
                    fail(file, f"canonical must use https://{SITE_HOST} without query or fragment")
            except ValueError:
                fail(file, "malformed canonical URL")
        for action in page.actions:
            labels = [action.label, " ".join(" ".join(action.text).split())]
            for label in labels:
                if PURCHASE_LABEL.fullmatch(label.strip(" \t\r\n→↗›»!")):
                    fail(file, f"line {action.line}: purchase action {label!r} is excluded")
                    break
        visible_text = " ".join(page.visible_text)
        match = PLACEHOLDER.search(visible_text)
        if match:
            fail(file, f"unresolved placeholder text {match.group()!r}")

    for file, page in pages.items():
        for reference in page.references:
            try:
                if reference.value.startswith(("javascript:", "vbscript:")):
                    fail(file, f"line {reference.line}: script URL in {reference.attribute}")
                    continue
                if not reference.value.strip():
                    fail(file, f"line {reference.line}: empty {reference.attribute}")
                    continue
                parsed = urlsplit(reference.value)
                if reference.attribute == "href" and purchase_path(parsed.path):
                    fail(file, f"line {reference.line}: purchase link {reference.value!r} is excluded")
                target, fragment = resolve_reference(dist, file, reference.value)
                if target is None:
                    external_count += 1
                    continue
                local_count += 1
                if not target.is_file():
                    fail(file, f"line {reference.line}: missing {reference.attribute} target {reference.value!r}")
                elif fragment and target.suffix.lower() == ".html":
                    target_page = pages.get(target)
                    if target_page is None or fragment not in target_page.ids:
                        fail(file, f"line {reference.line}: missing anchor {reference.value!r}")
            except ValueError as error:
                fail(file, f"line {reference.line}: invalid URL {reference.value!r}: {error}")

    if failures:
        print(f"FAIL: {len(failures)} issue(s) across {len(files)} HTML pages:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"PASS: {len(files)} HTML pages; {local_count} local references checked.")
    print("Canonical URLs, anchors, unique IDs, h1 headings, image alt attributes, and informational-only navigation passed.")
    print(f"External references skipped (no network requests): {external_count}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    return validate(parser.parse_args().dist)


if __name__ == "__main__":
    sys.exit(main())
