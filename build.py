#!/usr/bin/env python3
"""Render offer.json + theme into dist/index.html (single static file)."""
from __future__ import annotations
import json, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
THEMES = ROOT / "themes"
TEMPLATE = ROOT / "template" / "page.html"

def load_offer(path: Path) -> dict:
    data = json.loads(path.read_text())
    theme_id = data.get("theme") or "clean-dark"
    theme_path = THEMES / f"{theme_id}.json"
    if not theme_path.exists():
        raise SystemExit(f"Unknown theme {theme_id!r}. Available: {[p.stem for p in THEMES.glob('*.json')]}")
    theme = json.loads(theme_path.read_text())
    data["_theme"] = theme
    return data

def render(offer: dict) -> str:
    theme = offer["_theme"]
    colors = theme["colors"]
    fonts = theme["fonts"]
    brand = offer["brand"]
    o = offer["offer"]
    form = offer["form"]
    compliance = offer.get("compliance") or {}
    tpl = TEMPLATE.read_text()
    offer_json = json.dumps(offer, ensure_ascii=False)
    # Escape </script> in JSON
    offer_json = offer_json.replace("</", "<\\/")
    meta_desc = (o.get("subhead") or brand.get("tagline") or brand["name"])[:160]
    page_title = f'{brand["name"]} · Limited spots (preview)'
    replacements = {
        "{{THEME_COLOR}}": colors["bg"],
        "{{PAGE_TITLE}}": page_title,
        "{{META_DESC}}": meta_desc.replace('"', "'"),
        "{{GOOGLE_FONTS}}": fonts["google"],
        "{{C_BG}}": colors["bg"],
        "{{C_BG2}}": colors["bg2"],
        "{{C_CARD}}": colors["card"],
        "{{C_TEXT}}": colors["text"],
        "{{C_MUTED}}": colors["muted"],
        "{{C_ACCENT}}": colors["accent"],
        "{{C_ACCENT2}}": colors["accent2"],
        "{{C_DANGER}}": colors["danger"],
        "{{C_OK}}": colors["ok"],
        "{{C_BORDER}}": colors["border"],
        "{{C_GLOW}}": colors["glow"],
        "{{F_DISPLAY}}": fonts["display"],
        "{{F_ACCENT}}": fonts["accent"],
        "{{F_BODY}}": fonts["body"],
        "{{THEME_ID}}": theme["id"],
        "{{PREVIEW_BANNER}}": compliance.get("previewBanner") or "PREVIEW",
        "{{BRAND_NAME}}": brand["name"],
        "{{LEGAL_NAME}}": brand.get("legalName") or brand["name"],
        "{{PHONE}}": brand["phone"],
        "{{PHONE_TEL}}": brand["phoneTel"],
        "{{ADDRESS}}": brand.get("address") or "",
        "{{EYEBROW}}": o.get("eyebrow") or "LIMITED SPOTS",
        "{{HEADLINE}}": o["headline"],
        "{{SUBHEAD}}": o["subhead"],
        "{{REGULAR_PRICE}}": str(o.get("regularPrice") or "PLACEHOLDER"),
        "{{PROMO_PRICE}}": str(o.get("promoPrice") or "PLACEHOLDER"),
        "{{PRICE_NOTE}}": o.get("priceNote") or "",
        "{{CTA_PRIMARY}}": o.get("ctaPrimary") or "Claim a spot",
        "{{CTA_SECONDARY}}": o.get("ctaSecondary") or "See what's included",
        "{{DEADLINE_LABEL}}": o.get("deadlineLabel") or "Offer ends",
        "{{HOLD_MINUTES}}": str(o.get("holdMinutes") or 15),
        "{{FORM_TITLE}}": form.get("title") or "Reserve your spot",
        "{{FORM_LEDE}}": form.get("lede") or "",
        "{{CONSENT}}": form.get("consent") or "",
        "{{SUBMIT_LABEL}}": form.get("submitLabel") or "Hold my spot",
        "{{COMPLIANCE}}": compliance.get("footer") or "",
        "{{OFFER_JSON}}": offer_json,
    }
    out = tpl
    for k, v in replacements.items():
        out = out.replace(k, v)
    # robots meta already noindex in template; reinforce if flag false somehow
    if offer.get("noindex") is False:
        out = out.replace('content="noindex,nofollow"', 'content="index,follow"')
    return out

def build(offer_path: Path | None = None) -> Path:
    offer_path = offer_path or (ROOT / "offer.json")
    offer = load_offer(offer_path)
    DIST.mkdir(parents=True, exist_ok=True)
    html = render(offer)
    (DIST / "index.html").write_text(html)
    (DIST / "offer.json").write_text(json.dumps(offer, indent=2))
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    # Also copy theme id note
    (DIST / "BUILD.txt").write_text(
        f"Built from {offer_path.name}\ntheme={offer['theme']}\ndemoMode={offer.get('demoMode')}\nslug={offer.get('slug')}\n"
    )
    print(f"Built {DIST / 'index.html'} ({len(html)} bytes) theme={offer['theme']} demo={offer.get('demoMode')}")
    return DIST / "index.html"

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    build(path)
