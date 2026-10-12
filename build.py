#!/usr/bin/env python3
"""Build the whole collection into dist/ — the single folder you publish.

Every work keeps its own generator under works/<slug>/build.py. This script
runs all of them, copies the hand-written static files (CSS, JS, images) next
to the generated HTML, and then checks that every internal link in the built
site resolves to a file that exists.

Usage:
    python3 build.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
HUB = ROOT / "hub"
WORKS = ROOT / "works"
ORDER = ("friday", "parallelism", "torments")
STATIC = ("style.css", "script.js", "assets")
SKIP_SCHEMES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


def clean_dist() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)


def copy_static(source: Path, target: Path) -> None:
    """Copy the hand-written CSS/JS/images of one site into the built output."""
    target.mkdir(parents=True, exist_ok=True)
    for name in STATIC:
        item = source / name
        if item.is_dir():
            shutil.copytree(item, target / name)
        elif item.is_file():
            shutil.copy2(item, target / name)


def build_hub() -> None:
    """The hub is hand-written, not generated — copy it across as-is."""
    copy_static(HUB, DIST)
    shutil.copy2(HUB / "index.html", DIST / "index.html")


def build_work(slug: str) -> None:
    work = WORKS / slug
    result = subprocess.run(
        [sys.executable, str(work / "build.py")],
        cwd=work,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"{slug}: build failed\n{result.stderr.strip()}")
    print(f"  {result.stdout.strip()}")
    copy_static(work, DIST / slug)


class PageParser(HTMLParser):
    """Collects every href/src reference plus every id defined on the page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if not value:
                continue
            if name in ("href", "src"):
                self.refs.append((tag, name, value))
            elif name == "id":
                self.ids.add(value)


def check_links() -> int:
    """Every relative link and in-page anchor must resolve. Returns problem count."""
    pages: dict[Path, PageParser] = {}
    for path in sorted(DIST.rglob("*.html")):
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        pages[path] = parser

    problems: list[str] = []
    checked = 0
    for path, parser in pages.items():
        page = path.relative_to(DIST).as_posix()
        for tag, attr, value in parser.refs:
            if value.startswith(SKIP_SCHEMES):
                continue
            path_part, _, fragment = value.partition("#")
            if not path_part:  # same-page anchor, e.g. href="#friday"
                checked += 1
                if fragment and fragment not in parser.ids:
                    problems.append(f"{page}: {tag}[{attr}]='{value}' -> no element with id='{fragment}'")
                continue
            target = (path.parent / path_part).resolve()
            checked += 1
            if not target.exists():
                problems.append(f"{page}: {tag}[{attr}]='{value}' -> missing file")
                continue
            if fragment and target.suffix == ".html":
                target_page = pages.get(target)
                if target_page is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    target_page = target_parser
                if fragment not in target_page.ids:
                    problems.append(f"{page}: {tag}[{attr}]='{value}' -> no element with id='{fragment}'")

    for problem in problems:
        print(f"  BROKEN  {problem}")
    print(f"  checked {checked} links across {len(pages)} pages")
    return len(problems)


def link_external_sibling(slug: str, sibling_repo: str) -> None:
    """If a sibling repo's dist/ is on disk, expose it under dist/<slug>/.

    This is a post-build hook for cross-repo sub-sites that live in their
    own working tree but are served under the literature estate — the FBD
    being the example. Without it, ``clean_dist()`` runs first and the
    link-checker reports the link as broken even though it resolves on
    the live (or test) docroot via a symlink.

    The symlink is local-only; it is created in the ``dist`` working tree
    and is not staged in git. The link-checker accepts it because the
    resolved target exists.
    """
    sibling_dist = ROOT.parent / sibling_repo / "dist"
    target = DIST / slug
    if sibling_dist.is_dir() and not target.exists():
        target.symlink_to(sibling_dist.resolve())


def main() -> None:
    print(f"Building {ROOT.name} -> {DIST.relative_to(ROOT)}/")
    clean_dist()
    print(" hub")
    build_hub()
    for slug in ORDER:
        print(f" {slug}")
        build_work(slug)
    # Cross-repo siblings: expose them under dist/ before the link-checker runs.
    link_external_sibling("friday-bd", "friday-bande-dessinee")
    print(" links")
    broken = check_links()
    if broken:
        raise SystemExit(f"\n{broken} broken link(s) — fix before publishing.")


if __name__ == "__main__":
    main()