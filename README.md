# family-farm-preview — Obst Farm

Static website draft for **Obst Farm**, Daniel Obst's family farm in
**Fort Worth, Texas**, which sells **eggs and lamb** through **local pickup**
and **select farmers markets**. Plain HTML, CSS, and a small
progressive-enhancement script — no build step, no dependencies, no ordering
or payments.

> **Status: preview draft.** Every page carries `<meta name="robots" content="noindex, nofollow">`.
> The homepage headline still reads "Local Eggs & Lamb from Our Family Farm"
> (the approved working headline); the farm name appears in the header,
> footer, page titles, and meta descriptions.

## Structure

```
index.html                     Home  (/)
eggs-and-lamb/index.html       Eggs & Lamb  (/eggs-and-lamb/)
pickup-and-markets/index.html  Pickup & Markets  (/pickup-and-markets/)
assets/css/styles.css          All styles (palette, type, layout, hero crops)
assets/js/main.js              Mobile menu + scroll reveals (site works without it)
assets/images/                 Photos (currently illustrated placeholders)
tools/make-placeholders.py     Regenerates the placeholder images (needs Pillow)
.nojekyll                      Serve files as-is on GitHub Pages
```

All paths are relative, so the site works opened from a local server, under a
GitHub Pages repository subpath (`/family-farm-preview/`), or at the root of
its own domain later — no changes needed.

### Preview locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.

## Replacing a photo

1. Convert the real photo to WebP at (or near) the recommended size below.
   For example: `cwebp -q 80 photo.jpg -o farm-eggs.webp`, or export WebP from
   Photoshop, Affinity, Squoosh (squoosh.app), etc.
2. Give it **exactly the same filename**.
3. Replace the file in `assets/images/`.

The "PHOTO NEEDED" label is drawn inside each placeholder image, so it
disappears automatically when the file is replaced. Every frame reserves its
space with `width`/`height` attributes and CSS `aspect-ratio`, so swapping in a
photo won't shift the layout. Then update the alt text (below) so it describes
the real photo.

| File | Shot needed | Recommended size | Frame on page | Alt text lives in | Crop / position |
|---|---|---|---|---|---|
| `farm-pasture-hero.webp` | Wide farm or pasture view | 2400 × 1350 (16:9) | Full-bleed hero, Home | `index.html` (hero `<img>`) | `--hero-pos-desktop` and `--hero-pos-mobile` at the top of `assets/css/styles.css` |
| `farm-eggs.webp` | Close-up of eggs in a carton | 1600 × 1200 (4:3) | Home Eggs tile; Eggs section | `index.html` (Eggs tile) and `eggs-and-lamb/index.html` (`#eggs`) | `.tile__media img` and `.product__media img` use `object-fit: cover` (centred); add `object-position` there if needed |
| `farm-lamb.webp` | Packaged lamb as a customer receives it | 1600 × 1200 (4:3) | Home Lamb tile; Lamb section | `index.html` (Lamb tile) and `eggs-and-lamb/index.html` (`#lamb`) | same as eggs |
| `farm-family.webp` | Family doing farm chores — **only if approved for public use** | 1200 × 1500 (4:5 portrait) | Family story, Home | `index.html` (story `<img>`) | `.story__media img` |
| `farm-market.webp` | Farmers market booth | 1600 × 1000 (16:10) | Farmers markets section | `pickup-and-markets/index.html` (`#markets`) | `.markets__media img` |

**Hero crops:** the same hero file is shown wide on desktop and as a tall
portrait crop on phones. Tune each with the two CSS variables, e.g.
`--hero-pos-mobile: 35% 50%;` moves the phone crop left. Keep the main subject
roughly centred so both crops work. The headline and button are live HTML on
top of the photo, not part of the image.

If the family photo is **not** approved, delete the `<div class="story__media">`
block in `index.html`; the text column stands on its own.

## Logo

The header and footer show `assets/images/obst-farm-logo.svg`, currently a
dashed "OF" placeholder. When Daniel's clean logo file arrives:

1. Save it as `assets/images/obst-farm-logo.svg` (preferred) and replace the
   placeholder. If it's only a PNG, export it at least 320 px tall with a
   transparent background, name it `obst-farm-logo.png`, and change the six
   `src="…obst-farm-logo.svg"` references (header + footer on each page).
2. The logo slot is a fixed height (44 px in the header, 52 px in the
   footer). Width follows the logo's own proportions, capped by
   `--logo-max-w` (160 px), in `.brand__logo` in `assets/css/styles.css`.
3. The footer is dark green. If the logo is dark ink on transparent, use a
   light version there, or give `.brand__logo--footer` a cream background.
4. If the logo already includes the words "Obst Farm", remove the
   `<span>Obst Farm</span>` next to it so the name isn't shown twice.
5. Optionally replace `assets/images/favicon.svg` with a simplified logo mark.

## Claims and products to confirm with Daniel

The farm card mentions **grass-fed** and **pasture-raised**. The site
doesn't use either claim yet. Before adding them, Daniel should confirm which
product each one applies to (eggs, lamb, or both). Comments marking the
spots are in `index.html` (above the tiles) and `eggs-and-lamb/index.html`
(`EGG DETAILS` / `LAMB DETAILS`). Any other products on the card stay off the
site until Daniel confirms them; the site leads with eggs and lamb only.

## Updating market dates (one place)

Market dates live **only** in `pickup-and-markets/index.html`, between the
`MARKET DATES — EDIT HERE` and `END MARKET DATES` comments. That block includes
a copy-and-paste template for one market (name, date, hours, location, official
link). Until dates are confirmed the page shows "Upcoming market dates will be
posted here."

Other marked spots for confirmed details:

- `EGG DETAILS` / `LAMB DETAILS` comments in `eggs-and-lamb/index.html` —
  quantities, cuts, prices, availability.
- `PICKUP DETAILS` comment in `pickup-and-markets/index.html` — pickup
  instructions, hours, address (only if Daniel wants it public), and a
  call/text link once Daniel provides an approved business number.
- Family and faith wording comment in `index.html` ("Meet Daniel Obst" section).

## Behaviour notes

- Mobile menu: Menu / Close toggle button, Escape closes, focus stays inside
  while open. Without JavaScript the three links show as a plain list.
- Tiles stagger in on scroll; major sections fade up briefly. All of it is off
  for `prefers-reduced-motion`, and content is fully visible without JavaScript.
- Fonts: Fraunces (headings) and Source Sans 3 (body) from Google Fonts, with
  Georgia / system fallbacks.

## Going live later

1. Replace placeholders and fill in confirmed details.
2. Remove the `robots` `noindex` meta tag from each page.
3. Add a custom domain (GitHub Pages settings, or move the folder to any static host).
