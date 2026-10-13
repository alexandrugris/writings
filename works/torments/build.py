#!/usr/bin/env python3
"""Render the four supplied poems as one static reading page."""

from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SLUG = "torments"
OUTPUT = ROOT.parent.parent / "dist" / SLUG / "index.html"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT / "poems.md").read_text(encoding="utf-8")
EXPECTED = ["Impossibility", "Hurt", "Holding Hands", "Geometry"]
IMAGE = {
    "Impossibility": ("impossibility.webp", "Two people meet each other's gaze across a crowded dinner table."),
    "Hurt": ("hurt.webp", "Two people stand within a fragile, cracking cage of drawn domestic lines."),
    "Holding Hands": ("holding-hands.webp", "Two people sit apart on a bench while their hands remain clasped."),
    "Geometry": ("geometry.webp", "A precise geometric grid breaks into wild drawn lines and open landscape."),
}

poems = []
current = None
stanza = []


def flush_stanza():
    global stanza
    if current is not None and stanza:
        current["stanzas"].append(stanza)
    stanza = []


for raw in SOURCE.splitlines():
    line = raw.strip()
    title_match = re.fullmatch(r"\*\*([^*]+)\*\*|\*([^*]+)\*", line)
    if title_match and (title_match.group(1) or title_match.group(2)) in EXPECTED:
        flush_stanza()
        current = {"title": title_match.group(1) or title_match.group(2), "stanzas": []}
        poems.append(current)
    elif line == "---":
        flush_stanza()
    elif not line:
        flush_stanza()
    else:
        assert current is not None, f"Line before title: {line}"
        stanza.append(line)
flush_stanza()
assert [poem["title"] for poem in poems] == EXPECTED


def inline_markup(line):
    escaped = escape(line)
    return re.sub(r"\*([^*]+)\*", lambda match: f"<em>{match.group(1)}</em>", escaped)


def poem_body(poem):
    stanzas = []
    for stanza_lines in poem["stanzas"]:
        spans = "".join(f'<span class="verse-line">{inline_markup(line)}</span>' for line in stanza_lines)
        stanzas.append(f'<p class="stanza">{spans}</p>')
    return f'<div class="poem-body">{"".join(stanzas)}</div>'


def heading(title, index):
    visible = "<em>Geometry</em>" if title == "Geometry" else escape(title)
    return f'''<header class="poem-heading"><div class="poem-label"><span>{index:02d}</span><span class="label-line" aria-hidden="true"></span><span>04</span></div><h2 id="{title.lower().replace(' ', '-')}-title">{visible}</h2></header>'''


def figure(title):
    filename, alt = IMAGE[title]
    return f'''<figure class="poem-art"><div class="art-frame"><img src="assets/{filename}" alt="{escape(alt)}" loading="lazy" decoding="async"></div><figcaption>{escape(title)} <span aria-hidden="true">/ sketch</span></figcaption></figure>'''


parts = []
for index, poem in enumerate(poems, start=1):
    title = poem["title"]
    slug = title.lower().replace(" ", "-")
    if index == 1:
        inner = f'<div class="first-inner">{heading(title,index)}{poem_body(poem)}</div>'
        cls = "poem-first"
    elif index in (2, 3):
        inner = f'<div class="split-inner"><div class="poem-copy">{heading(title,index)}{poem_body(poem)}</div>{figure(title)}</div>'
        cls = "poem-split" + (" image-left" if index == 2 else " image-right")
    else:
        inner = f'<div class="geometry-image">{figure(title)}</div><div class="geometry-inner">{heading(title,index)}{poem_body(poem)}</div>'
        cls = "poem-geometry"
    parts.append(f'<section class="poem-section {cls}" id="{slug}" aria-labelledby="{slug}-title">{inner}</section>')

word_count = len(re.findall(r"\b[\w’'-]+\b", SOURCE))
minutes = max(1, round(word_count / 180))

html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="/assets/favicon.svg?v=2" type="image/svg+xml">
  <link rel="icon" href="/assets/favicon-32x32.png?v=2" sizes="32x32" type="image/png">
  <link rel="icon" href="/assets/favicon-16x16.png?v=2" sizes="16x16" type="image/png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=2">
  <meta name="theme-color" content="#f4f4f4">
  <meta name="description" content="Torments: four illustrated poems — Impossibility, Hurt, Holding Hands, and Geometry.">
  <title>Torments — Four Illustrated Poems</title>
  <link rel="canonical" href="https://alexandrugris.ro/literature/torments/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Alexandru Gris">
  <meta property="og:locale" content="en_GB">
  <meta property="og:title" content="Torments — Four Illustrated Poems">
  <meta property="og:description" content="Torments: four illustrated poems — Impossibility, Hurt, Holding Hands, and Geometry.">
  <meta property="og:url" content="https://alexandrugris.ro/literature/torments/">
  <meta property="og:image" content="https://alexandrugris.ro/literature/assets/og-torments.jpg">
  <meta property="og:image:secure_url" content="https://alexandrugris.ro/literature/assets/og-torments.jpg">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Charcoal drawing of two figures sitting apart on a bench in a winter landscape.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Torments — Four Illustrated Poems">
  <meta name="twitter:description" content="Torments: four illustrated poems — Impossibility, Hurt, Holding Hands, and Geometry.">
  <meta name="twitter:image" content="https://alexandrugris.ro/literature/assets/og-torments.jpg">
  <meta name="twitter:image:alt" content="Charcoal drawing of two figures sitting apart on a bench in a winter landscape.">
  <link rel="preload" as="image" href="assets/impossibility.webp">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#poems">Skip to poems</a>
  <div class="progress" aria-hidden="true"><span id="progress-fill"></span></div>
  <header class="site-header"><a class="brand" href="#top" aria-label="Torments, back to top">T<span>/</span></a><span class="site-caption">Four illustrated poems</span><nav class="section-nav" aria-label="Poems"><a href="#impossibility">I <span>Impossibility</span></a><a href="#hurt">II <span>Hurt</span></a><a href="#holding-hands">III <span>Holding Hands</span></a><a href="#geometry">IV <span>Geometry</span></a></nav></header>

  <main id="top">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-content">
        <p class="hero-kicker">A cycle of four poems</p>
        <h1 id="hero-title">Torments<span>.</span></h1>
        <p class="hero-deck">Four poems from one period of life.</p>
        <a class="hero-read" href="#poems">Begin reading <span aria-hidden="true">↘</span></a>
        <div class="hero-index"><span>01</span><span>Impossibility</span><span aria-hidden="true">—</span><span>04</span><span>Geometry</span></div>
      </div>
      <figure class="hero-figure">
        <img class="hero-image" src="assets/impossibility.webp" alt="Two people exchange a charged glance across a crowded dinner table." fetchpriority="high">
        <figcaption>I / Impossibility</figcaption>
      </figure>
    </section>
    <div class="collection-intro" id="poems"><span>01 — 04</span><p>Impossibility <i aria-hidden="true">/</i> Hurt <i aria-hidden="true">/</i> Holding Hands <i aria-hidden="true">/</i> Geometry</p><span>~{minutes} min read</span></div>
    {''.join(parts)}
    <div class="endpiece"><span class="end-mark" aria-hidden="true">✳</span><p>End of collection</p><a href="#top">Back to the beginning <span aria-hidden="true">↑</span></a></div>
  </main>
  <footer class="site-footer">
    <span>Torments</span>
    <nav class="works-nav" aria-label="The collection">
      <a href="../index.html">All works</a>
      <a href="../friday/index.html">Friday</a>
      <a href="../parallelism/index.html">Parallelism</a>
    </nav>
    <span>Black &amp; white sketches</span>
  </footer>
  <script src="script.js" defer></script>
</body>
</html>'''

OUTPUT.write_text(html, encoding="utf-8")
print(f"Built {len(poems)} poems, {sum(len(stanza) for poem in poems for stanza in poem['stanzas'])} lines, {word_count} words")
