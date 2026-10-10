#!/usr/bin/env python3
"""Convert the sketches to grayscale WebP.

Every image on the site is rendered through `filter: grayscale(1)` (see the
`style.css` of each work), so the colour data in the PNGs is never displayed —
it is pure weight. This script bakes the same luma conversion into the file and
encodes WebP at quality 82, which is visually indistinguishable from the source
at 100% while being roughly nine times smaller.

It replaces `foo.png` with `foo.webp` in `hub/assets` and `works/*/assets`. The
references in `hub/index.html` and the `build.py` of each work still point at
`.png` afterwards — `python3 build.py` will report them as broken links, which
is the intended safety net. Fix them (or let a search-and-replace do it) and
commit both.

Usage:
    python3 tools/optimize_images.py            # convert PNG -> WebP
    python3 tools/optimize_images.py --dry-run  # only report the savings
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALITY = 82
ASSET_DIRS = (ROOT / "hub" / "assets", *(ROOT / "works").glob("*/assets"))


def convert(png: Path, workdir: Path, dry_run: bool) -> int:
    """Grayscale-encode one PNG to WebP and drop the original. Returns bytes saved."""
    gray = workdir / (png.stem + "-gray.png")
    webp = png.with_suffix(".webp")

    from PIL import Image

    with Image.open(png) as image:
        image.convert("L").save(gray)

    if dry_run:
        before = png.stat().st_size
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(QUALITY), "-m", "6", "-sharp_yuv", str(gray), "-o", str(webp)],
            check=True,
        )
        after = webp.stat().st_size
        webp.unlink()
        return before - after

    subprocess.run(
        ["cwebp", "-quiet", "-q", str(QUALITY), "-m", "6", "-sharp_yuv", str(gray), "-o", str(webp)],
        check=True,
    )
    gray.unlink()
    before = png.stat().st_size
    after = webp.stat().st_size
    png.unlink()
    return before - after


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    pngs = sorted(p for directory in ASSET_DIRS if directory.is_dir() for p in directory.glob("*.png"))
    if not pngs:
        print("No PNG left — everything is already WebP.")
        return

    saved = 0
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for png in pngs:
            gain = convert(png, workdir, dry_run)
            saved += gain
            mark = "would save" if dry_run else "saved"
            print(f"  {png.relative_to(ROOT).as_posix():42s} -> {png.stem}.webp   {mark} {gain // 1024}K")

    verb = "would save" if dry_run else "saved"
    print(f"\n{verb} {saved // (1024 * 1024)} MB in total")


if __name__ == "__main__":
    main()