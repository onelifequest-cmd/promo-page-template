# Limited-spots promo page template

Reusable single-file promo page for MERKABA / Conquest AI offers: limited spots, countdown, 15-minute hold, themed form, Stripe Payment Link handoff.

Inspired by the *mechanics* of limited-spot offer pages (spots counter, hold, countdown, single HTML file). All branding, copy, SVGs, and code here are original.

## What's in the box

| Path | Role |
|---|---|
| `offer.json` | Drives the whole page (brand, prices, spots, deadline, copy, FAQ, payment link, theme) |
| `themes/halloween.json` | Spooky seasonal pack (embers, lantern motif, Creepster/IM Fell) |
| `themes/clean-dark.json` | Year-round Conquest-style dark/blue pack |
| `template/page.html` | One HTML shell; build injects config |
| `build.py` | Renders `offer.json` → `dist/index.html` |
| `server/app.py` | Optional real API: `GET /api/info`, `POST /api/lead`, `GET /api/status` |
| `instances/conquest-ai/` | First example offer (PLACEHOLDER prices) |
| `dist/` | Built static output (deploy this) |

## Make a new page (short)

1. **Copy config**
   ```bash
   cp offer.json instances/my-offer/offer.json
   # or start from instances/conquest-ai/offer.json
   ```
2. **Edit `offer.json`**
   - `brand.*` — name, phone, address
   - `offer.regularPrice` / `promoPrice` / `spotsTotal` / `deadline` / `paymentLink`
   - `theme` — `"halloween"` or `"clean-dark"`
   - `features`, `steps`, `faq`, compliance footer
   - Set `demoMode: false` when you wire the real server
3. **Build**
   ```bash
   python3 build.py instances/my-offer/offer.json
   # writes dist/index.html
   ```
4. **Preview locally**
   - Static + demo API (browser localStorage): open `dist/index.html` or any static server.
   - Real holds API:
     ```bash
     pip install -r server/requirements.txt
     PROMO_OFFER=instances/my-offer/offer.json python3 server/app.py
     # http://127.0.0.1:5055
     ```
5. **Deploy** the `dist/` folder as a Render static site (or any static host). Keep `noindex` until Patrick says publish.

## Demo mode vs real API

- **`demoMode: true`** (default for previews): the page mocks `/api/info`, `/api/lead`, `/api/status` in the browser with `localStorage`. Holds expire client-side. Banner says DEMO MODE.
- **`demoMode: false`**: the page calls the real server routes. Run `server/app.py` (or deploy it as a web service) and point static assets at the same origin.

Payment is always a URL from `offer.paymentLink`. This template **never** creates Stripe products, prices, or Payment Links.

## PLACEHOLDER fields (need Patrick's decision)

Before any real publish, set in `offer.json`:

- `offer.regularPrice` / `offer.promoPrice`
- `offer.spotsTotal`
- `offer.deadline` (ISO 8601 with offset; page timezone label uses `brand.timezone`)
- `offer.paymentLink` — existing Stripe Payment Link URL only

## Compliance notes (Conquest AI example)

- No “85% of missed callers” claim
- No response-time or results guarantees
- Say **your CRM**, never HighLevel
- Do not mention Scores OS
- Preview ships with `<meta name="robots" content="noindex">`

## Themes

Switch with `"theme": "halloween"` or `"theme": "clean-dark"`. Add a new JSON under `themes/` and point `offer.theme` at its id.
