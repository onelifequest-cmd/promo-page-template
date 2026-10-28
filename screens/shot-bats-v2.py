import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
OUT = Path(__file__).resolve().parent

FORCE_MID = """() => {
  const bats = [...document.querySelectorAll('.abat')];
  // Keep mid-flight but avoid sitting on primary CTA / headline center
  const places = [
    [8, 8, 1], [78, 12, -1], [6, 58, 1], [88, 48, -1]
  ];
  bats.forEach((el, i) => {
    el.style.animation = 'none';
    el.style.opacity = '0.98';
    const [x, y, face] = places[i % places.length];
    const flip = face < 0 ? ' scaleX(-1)' : '';
    el.style.transform = `translate(${x}vw, ${y}vh) rotate(${face*6}deg)${flip}`;
  });
  return {count: bats.length, w: bats[0] && getComputedStyle(bats[0]).width};
}"""

async def main():
    report = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            headless=True,
        )
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.emulate_media(reduced_motion="no-preference")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(500)
        report.append(f"desktop: {await page.evaluate(FORCE_MID)}")
        await page.wait_for_timeout(120)
        await page.screenshot(path=str(OUT / "bats-v2-d1280-midflight.png"), full_page=False)

        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(200)
        await page.fill('#f-name', 'Bat V2')
        await page.fill('#f-phone', '4078639276')
        await page.fill('#f-email', 'bat-v2@example.com')
        await page.check('#f-consent')
        await page.click('#submit')
        await page.wait_for_timeout(900)
        report.append(f"delivery: {await page.evaluate('''() => { const d=document.querySelector('.dbat'); if(!d) return null; const r=d.getBoundingClientRect(); return {w:r.width,h:r.height,cls:d.className}; }''')}")
        await page.screenshot(path=str(OUT / "bats-v2-d1280-delivery.png"), full_page=False)
        await ctx.close()

        ctx = await browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        await page.emulate_media(reduced_motion="no-preference")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(400)
        report.append(f"phone: {await page.evaluate(FORCE_MID)}")
        await page.wait_for_timeout(120)
        await page.screenshot(path=str(OUT / "bats-v2-p390-midflight.png"), full_page=False)

        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(200)
        await page.fill('#f-name', 'Bat V2 Phone')
        await page.fill('#f-phone', '4078639276')
        await page.fill('#f-email', 'bat-v2p@example.com')
        await page.check('#f-consent')
        await page.click('#submit')
        await page.wait_for_timeout(900)
        await page.screenshot(path=str(OUT / "bats-v2-p390-delivery.png"), full_page=False)
        await ctx.close()
        await browser.close()
    print("\n".join(report))

asyncio.run(main())
