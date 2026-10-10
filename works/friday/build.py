#!/usr/bin/env python3
"""Turn the supplied story into a static, accessible reading page."""

from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SLUG = "friday"
SOURCE = ROOT / "story.txt"
OUTPUT = ROOT.parent.parent / "dist" / SLUG / "index.html"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

CHAPTERS = {
    "Friday": ("I", "Friday", "The long way home"),
    "Saturday": ("II", "Saturday", "A day to fill"),
    "Sunday": ("III", "Sunday", "The weather inside"),
    "Later": ("IV", "Later", "A room for someone else"),
}

ILLUSTRATIONS = {
    ("Friday", "9:30 PM"): ("doner-shop.webp", "A table for one", "A man and a woman sit apart in a late-night fast-food shop."),
    ("Saturday", "9:00 PM"): ("lovers-become-trees.webp", "The lovers become trees", "An elderly couple on a bench take root beneath two intertwined trees."),
    ("Sunday", "10:00 AM"): ("winter-room.webp", "Winter in the room", "An empty apartment and a window covered by a blizzard."),
}


def paragraph(text):
    lines = [line.strip() for line in text.strip().splitlines()]
    is_verse = len(lines) > 1 and any(len(line) < 65 for line in lines)
    inner = "<br>".join(escape(line) for line in lines)
    return f'<p class="{"verse" if is_verse else ""}">{inner}</p>'


def figure(filename, title, alt, special=False):
    cls = "story-figure feature-figure" if special else "story-figure"
    extra = ('<blockquote class="tree-quote">“I think all true lovers eventually become trees.”</blockquote>'
             if special else "")
    return f'''<figure class="{cls}">
      <div class="image-frame"><img src="assets/{filename}" alt="{escape(alt)}" loading="lazy" decoding="async"></div>
      <figcaption><span class="figure-rule" aria-hidden="true"></span>{escape(title)}</figcaption>
      {extra}
    </figure>'''


text = SOURCE.read_text(encoding="utf-8").strip()
blocks = re.split(r"\n\s*\n", text)
chapter = None
time = None
scene_parts = []
chapter_parts = []
html_parts = []
scene_number = 0


def flush_scene():
    global scene_parts, scene_number
    if not scene_parts:
        return
    scene_number += 1
    scene_id = f'{chapter.lower()}-{scene_number}'
    label = time or "Epilogue"
    content = "\n".join(scene_parts)
    visual = ILLUSTRATIONS.get((chapter, time))
    if visual:
        content += "\n" + figure(*visual, special=(chapter == "Saturday" and time == "9:00 PM"))
    chapter_parts.append(f'''<article class="scene" id="{scene_id}">
      <div class="scene-marker"><span class="marker-dot" aria-hidden="true"></span><time>{escape(label)}</time></div>
      <div class="scene-content">{content}</div>
    </article>''')
    scene_parts = []


def flush_chapter():
    global chapter_parts, scene_number
    if chapter is None:
        return
    flush_scene()
    roman, name, subtitle = CHAPTERS[chapter]
    html_parts.append(f'''<section class="chapter" id="{chapter.lower()}" aria-labelledby="{chapter.lower()}-title">
      <header class="chapter-heading">
        <span class="chapter-index">Part {roman} <span aria-hidden="true">/</span> IV</span>
        <h2 id="{chapter.lower()}-title">{name}</h2>
        <p>{subtitle}</p>
      </header>
      <div class="scenes">{"".join(chapter_parts)}</div>
    </section>''')
    chapter_parts = []
    scene_number = 0


for block in blocks:
    block = block.strip()
    if block == "Friday" or re.fullmatch(r"## (Saturday|Sunday|Later)", block):
        flush_chapter()
        chapter = block.removeprefix("## ")
        time = None
    elif re.fullmatch(r"\*\*\d{1,2}:\d{2} (?:AM|PM)\*\*", block):
        flush_scene()
        time = block.strip("*")
    else:
        scene_parts.append(paragraph(block))
flush_chapter()

word_count = len(re.findall(r"\b[\w’'-]+\b", text))
reading_minutes = round(word_count / 220)

page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f5f5f5">
  <meta name="description" content="Friday: an illustrated story of solitude, imagined love, changing weather, and the lives that fill a room.">
  <title>Friday — An Illustrated Story</title>
  <link rel="preload" as="image" href="assets/rain-walk.webp">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#story">Skip to story</a>
  <div class="reading-progress" aria-hidden="true"><span id="progress-fill"></span></div>
  <header class="site-header">
    <a class="wordmark" href="#top" aria-label="Friday, back to top">F<span class="wordmark-stroke">/</span></a>
    <span class="header-caption">An illustrated story</span>
    <nav class="chapter-nav" aria-label="Chapters">
      <a href="#friday">01 <span>Friday</span></a>
      <a href="#saturday">02 <span>Saturday</span></a>
      <a href="#sunday">03 <span>Sunday</span></a>
      <a href="#later">04 <span>Later</span></a>
    </nav>
  </header>

  <main id="top">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <div class="hero-kicker"><span class="hand-drawn-line" aria-hidden="true"></span> A story in four movements</div>
        <h1 id="hero-title">Friday<span class="title-period">.</span></h1>
        <p class="hero-deck">Undefined gray days under an undefined gray sky.</p>
        <div class="hero-bottom">
          <a class="read-link" href="#story"><span>Begin reading</span><span class="arrow" aria-hidden="true">↘</span></a>
          <span class="read-time">~{reading_minutes} min read</span>
        </div>
      </div>
      <figure class="hero-art">
        <img src="assets/rain-walk.webp" alt="A solitary figure walks a rain-soaked city street beneath umbrellas and tram wires." fetchpriority="high">
        <figcaption>Fig. 01 <span aria-hidden="true">—</span> The walk home</figcaption>
      </figure>
      <div class="hero-vertical" aria-hidden="true">Rain / longing / time</div>
    </section>

    <div class="story-intro" id="story">
      <div class="story-intro-number" aria-hidden="true">01—04</div>
      <div><p class="eyebrow">The story</p><p>Three days. A room. The weather keeps changing.</p></div>
      <span class="intro-endmark" aria-hidden="true">✳</span>
    </div>

    {''.join(html_parts)}

    <div class="endpiece" aria-label="End of story">
      <span class="endpiece-mark" aria-hidden="true">✳</span>
      <p>End of story</p>
      <a href="#top">Back to the beginning <span aria-hidden="true">↑</span></a>
    </div>
  </main>
  <footer class="site-footer">
    <span>Friday</span>
    <nav class="works-nav" aria-label="The collection">
      <a href="../index.html">All works</a>
      <a href="../parallelism/index.html">Parallelism</a>
      <a href="../torments/index.html">Torments</a>
    </nav>
    <span>Illustrated in black &amp; white</span>
  </footer>
  <script src="script.js" defer></script>
</body>
</html>'''

OUTPUT.write_text(page, encoding="utf-8")
print(f"Built {OUTPUT} from {word_count} story words and {len(html_parts)} chapters")
