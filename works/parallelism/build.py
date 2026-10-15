#!/usr/bin/env python3
"""Build the supplied poem as a static reading page without assigning speakers."""

from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SLUG = "parallelism"
OUTPUT = ROOT.parent.parent / "dist" / SLUG / "index.html"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
source = (ROOT / "poem.txt").read_text(encoding="utf-8").strip()
lines = source.splitlines()
assert lines[0].strip() == "Parallelism"

calls = []
current = None
for raw in lines[1:]:
    line = raw.strip()
    if not line:
        continue
    if re.fullmatch(r"\*\*\d{1,2}:\d{2} (?:AM|PM)\*\*", line):
        current = {"time": line.strip("*"), "stage": "", "dialogue": []}
        calls.append(current)
    elif re.fullmatch(r"\*[^*]+\*", line):
        assert current is not None
        current["stage"] = line.strip("*")
    else:
        assert current is not None
        current["dialogue"].append(line)

assert len(calls) == 3 and all(call["stage"] for call in calls)


def render_line(line, call_number):
    if line == "…":
        return '<p class="pause" aria-label="pause">…</p>'
    if line == "She:":
        return '<p class="speaker-note">She:</p>'
    classes = ["utterance"]
    if line == "I love you. I don’t want to be your friend.":
        classes.append("confession")
    if call_number == 3 and line == "Bye.":
        classes.append("farewell")
    return f'<p class="{" ".join(classes)}">{escape(line)}</p>'


roman = ["I", "II", "III"]
rendered_calls = []
for index, call in enumerate(calls, start=1):
    illustration = ""
    if index == 2:
        illustration = '''<figure class="call-figure two-rooms">
            <div class="figure-frame"><img src="assets/two-rooms.webp" alt="Two people in separate rooms look at their phones across a wide blank space." loading="lazy" decoding="async"></div>
            <figcaption>Two rooms, one conversation <span aria-hidden="true">/ 02</span></figcaption>
          </figure>'''
    dialogue = "\n".join(render_line(line, index) for line in call["dialogue"])
    rendered_calls.append(f'''<section class="call call-{index}" id="call-{index}" aria-labelledby="call-{index}-title">
      <div class="call-head">
        <span class="call-number">Conversation {roman[index-1]} <span aria-hidden="true">/</span> III</span>
        <div class="call-head-main"><p class="call-time">{escape(call["time"])}</p><h2 id="call-{index}-title">{escape(call["stage"])}</h2></div>
        <span class="call-glyph" aria-hidden="true">∥</span>
      </div>
      {illustration}
      <div class="dialogue-wrap"><div class="dialogue" aria-label="Conversation {index}">{dialogue}</div></div>
    </section>''')

word_count = len(re.findall(r"\b[\w’'-]+\b", source))
read_minutes = max(1, round(word_count / 200))

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
  <meta name="description" content="Parallelism: two voices in three late-night conversations, told as an illustrated dialogue.">
  <title>Parallelism — Two Voices</title>
  <link rel="canonical" href="https://alexandrugris.ro/literature/parallelism/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Alexandru Gris">
  <meta property="og:locale" content="en_GB">
  <meta property="og:title" content="Parallelism — Two Voices">
  <meta property="og:description" content="Parallelism: two voices in three late-night conversations, told as an illustrated dialogue.">
  <meta property="og:url" content="https://alexandrugris.ro/literature/parallelism/">
  <meta property="og:image" content="https://alexandrugris.ro/literature/assets/og-parallelism.jpg">
  <meta property="og:image:secure_url" content="https://alexandrugris.ro/literature/assets/og-parallelism.jpg">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Charcoal drawing of two people in separate rooms, each lit by the glow of a phone.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Parallelism — Two Voices">
  <meta name="twitter:description" content="Parallelism: two voices in three late-night conversations, told as an illustrated dialogue.">
  <meta name="twitter:image" content="https://alexandrugris.ro/literature/assets/og-parallelism.jpg">
  <meta name="twitter:image:alt" content="Charcoal drawing of two people in separate rooms, each lit by the glow of a phone.">
  <link rel="preload" as="image" href="assets/phone-lights-up.webp">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#poem">Skip to the dialogue</a>
  <div class="progress" aria-hidden="true"><span id="progress-fill"></span></div>
  <header class="site-header">
    <a class="monogram" href="#top" aria-label="Parallelism, back to top">∥</a>
    <span class="site-kind">An illustrated dialogue</span>
    <nav class="call-nav" aria-label="Conversations">
      <a href="#call-1">I <span>1:00 AM</span></a>
      <a href="#call-2">II <span>12:00 AM</span></a>
      <a href="#call-3">III <span>12:00 AM</span></a>
    </nav>
  </header>

  <main id="top">
    <section class="hero" aria-labelledby="title">
      <div class="hero-copy">
        <p class="kicker"><span aria-hidden="true">↳</span> Dialogue / three conversations</p>
        <h1 id="title"><span>Parallel</span><span>ism<span class="title-dot">.</span></span></h1>
        <p class="hero-description">A phone lights up. Then it lights up again.</p>
        <div class="hero-foot"><a class="begin-link" href="#poem">Begin reading <span aria-hidden="true">↘</span></a><span>~{read_minutes} min read</span></div>
      </div>
      <figure class="hero-figure"><img src="assets/phone-lights-up.webp" alt="A person on a bed looks at a glowing phone while an empty chair faces them across the room." fetchpriority="high"><figcaption>01 / The phone lights up</figcaption></figure>
      <div class="hero-lines" aria-hidden="true"><i></i><i></i></div>
    </section>

    <div class="poem-intro" id="poem"><span>01 — 03</span><p>Two voices, separated by what they say and what they cannot ask.</p><span class="intro-mark" aria-hidden="true">∥</span></div>

    {''.join(rendered_calls)}

    <figure class="closing-figure"><img src="assets/parallel-paths.webp" alt="Two figures walk separate paths toward a shared horizon under telephone wires." loading="lazy" decoding="async"><figcaption>Two paths <span aria-hidden="true">/ 03</span></figcaption></figure>
    <div class="endpiece"><span aria-hidden="true">∥</span><p>End of the dialogue</p><a href="#top">Back to the beginning <span aria-hidden="true">↑</span></a></div>
  </main>
  <footer class="site-footer">
    <span>Parallelism</span>
    <nav class="works-nav" aria-label="The collection">
      <a href="../index.html">All works</a>
      <a href="../friday/index.html">Friday</a>
      <a href="../torments/index.html">Torments</a>
    </nav>
    <span>Black &amp; white sketches</span>
  </footer>
  <script src="script.js" defer></script>
</body>
</html>'''

OUTPUT.write_text(html, encoding="utf-8")
print(f"Built three conversations, {sum(len(c['dialogue']) for c in calls)} dialogue lines, {word_count} words")
