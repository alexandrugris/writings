# Writings

Friday, Parallelism and Torments — three illustrated works in one static site.

Everything is plain HTML, CSS, JS and images: no framework, no dependencies,
nothing to install. You edit the text, run one command, and publish `dist/`.

## Layout

```
build.py                 build everything + verify links
hub/                     the collection page ("Writings")
  index.html             links to the three works
  style.css
  assets/                cover sketches used by the hub
works/
  friday/                story.txt + build.py + style.css + script.js + assets/
  parallelism/           poem.txt + build.py + style.css + script.js + assets/
  torments/              poems.md + build.py + style.css + script.js + assets/
dist/                    build output — this is what you publish
  index.html             the hub, at /
  friday/index.html      at /friday/
  parallelism/index.html at /parallelism/
  torments/index.html    at /torments/
```

`dist/` is committed, so you can deploy straight from the repository.

## Build

```bash
python3 build.py
```

This regenerates each work's HTML from its text source, copies the CSS, JS and
images into `dist/`, then walks every page and fails if any link, image or
in-page anchor points at something that does not exist.

## Publish

`dist/` works from the root of any static host, and also from a subdirectory,
because every link is relative.

- **Netlify / Cloudflare Pages** — drop the `dist` folder, or point the build
  command at `python3 build.py` and the publish directory at `dist`.
- **GitHub Pages** — push, then Settings → Pages → deploy from a branch, folder
  `/dist`. The site will live under `https://<user>.github.io/<repo>/` and all
  relative links still work.
- **Any web server** — copy `dist/` into the document root.

Local preview:

```bash
python3 -m http.server --directory dist 8000
```

Opening `dist/index.html` straight from Finder works too; that is why the links
are written as `friday/index.html` rather than `friday/`. Switch them to
`friday/` if you only care about cleaner URLs on a host that resolves directory
indexes.

## Editing

| To change | Edit |
| --- | --- |
| The story | `works/friday/story.txt` |
| The poem | `works/parallelism/poem.txt` |
| The four poems | `works/torments/poems.md` |
| A page's wording or structure | the `page = f'''...'''` template in that work's `build.py` |
| Cover text or descriptions | `hub/index.html` |
| Styling | the `style.css` next to it |

After any change: `python3 build.py`, then commit both the source and `dist/`.