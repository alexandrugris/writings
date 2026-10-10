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

## Deploying to alexandrugris.ro

Live at **https://alexandrugris.ro/literature/**, served from the `literature/`
subdirectory of that site's docroot on the Hetzner VPS.

`alexandrugris.ro` is self-hosted — do **not** use `website_deploy`, which would
publish a copy somewhere else. Deploy by rsync over the `website-root` alias
from `~/.ssh/config` (Tailscale; the public port 22 is firewalled). The full
procedure lives in `~/Downloads/Personal Website/AGENTS.md`; this is the part
that applies here:

```bash
python3 build.py                                  # always rebuild first

TS=$(date +%Y%m%d-%H%M%S)
ssh website-root "cp -a /var/www/html /var/www/backup-$TS"

rsync -avz dist/ website-root:/var/www/html/literature/

ssh website-root 'chown -R root:root /var/www/html/literature && \
  find /var/www/html/literature -type d -exec chmod 755 {} + && \
  find /var/www/html/literature -type f -exec chmod 644 {} +'
```

`dist/` carries the trailing slash so its *contents* become the contents of
`literature/` — that is the one form of the flattening trap that is correct
here. Do not add `--delete` casually: it will remove anything else that ends up
in the directory. Scope every `chown`/`chmod` to `literature/`; a bare
`/var/www/html` sweep would reach into the personal site and `from-the-edges/`.

Verify afterwards over HTTPS: the four pages and all fourteen `.webp` files must
match the local build by md5, every `content-type` must be right, and a headless
pass should click hub → work → back with no failed requests.

The nginx vhost caches `.png`, `.jpg` and `.gif` for 84 days but **not** `.webp`,
so artwork changes appear immediately.

## Images

The sketches are stored as **grayscale WebP at quality 82**. Every image on the
site is rendered through `filter: grayscale(1)` in CSS, so the colour in the
originals was never displayed — only weight. Baking the grayscale in and
encoding WebP takes the artwork from 48 MB to 4.7 MB with no visible change at
100% zoom. Dimensions are untouched, so nothing was resampled.

Got a new sketch? Drop the PNG in `hub/assets/` or `works/<slug>/assets/`, point
the page at it, then:

```bash
python3 tools/optimize_images.py
```

It grayscales and converts every PNG it finds and deletes the original. Until
you fix the reference, `python3 build.py` will report the `.png` as a broken
link — that is the safety net. The colour originals live in the git history and
in the untouched clones under `../originals/`.

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