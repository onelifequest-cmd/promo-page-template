import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

async def main():
    report = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            headless=True,
        )
        # Desktop 1280
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)
        layout = await page.evaluate("""() => {
          const h1 = document.querySelector('h1');
          const card = document.querySelector('.hero-card');
          const banner = document.querySelector('.preview-banner');
          const sticky = document.querySelector('.sticky');
          const rects = {};
          for (const [k,el] of Object.entries({h1, card, banner})) {
            if (!el) { rects[k]=null; continue; }
            const r = el.getBoundingClientRect();
            rects[k] = {top:r.top, left:r.left, w:r.width, h:r.height, bottom:r.bottom, right:r.right};
          }
          return {
            title: document.title,
            banner: banner && banner.innerText.slice(0,120),
            count: document.getElementById('count') && document.getElementById('count').innerText,
            priceNow: document.getElementById('priceNow') && document.getElementById('priceNow').innerText,
            rects,
            overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
          };
        }""")
        report.append(f"desktop: {layout}")
        await page.screenshot(path=str(OUT / "d1280-top.png"), full_page=False)
        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'start'})")
        await page.wait_for_timeout(600)
        await page.screenshot(path=str(OUT / "d1280-claim.png"), full_page=False)
        await ctx.close()

        # Phone 390
        ctx = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
        )
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)
        phone = await page.evaluate("""() => {
          const issues = [];
          const els = [...document.querySelectorAll('h1, .hero-card, .btn-primary, .preview-banner, .phone-pill, .topbar')];
          for (const el of els) {
            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            if (r.right > window.innerWidth + 1) issues.push('overflow:'+(el.id||el.className));
            if (cs.opacity === '0') issues.push('invisible:'+(el.id||el.className));
          }
          // check overlap: phone pill vs logo
          const logo = document.querySelector('.logo');
          const pill = document.querySelector('.phone-pill');
          let overlap = false;
          if (logo && pill) {
            const a = logo.getBoundingClientRect(), b = pill.getBoundingClientRect();
            overlap = !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
          }
          return {
            overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
            issues,
            overlapLogoPill: overlap,
            bodyW: document.documentElement.scrollWidth,
            vw: window.innerWidth,
          };
        }""")
        report.append(f"phone layout: {phone}")
        await page.screenshot(path=str(OUT / "p390-top.png"), full_page=False)
        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'start'})")
        await page.wait_for_timeout(600)
        await page.screenshot(path=str(OUT / "p390-claim.png"), full_page=False)
        # scroll mid features
        await page.evaluate("document.getElementById('included').scrollIntoView({block:'start'})")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / "p390-included.png"), full_page=False)
        await ctx.close()
        await browser.close()
    Path("/tmp/promo-shot-report.txt").write_text("\n".join(report))
    print("\n".join(report))

asyncio.run(main())
