import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
OUT = Path(__file__).resolve().parent

FORCE_MID = """() => {
  const bats = [...document.querySelectorAll('.abat')];
  // Pause CSS animation and place bats visibly mid-screen on varied paths
  const places = [
    [18, 14, 1], [62, 22, -1], [40, 58, 1], [78, 48, -1]
  ];
  bats.forEach((el, i) => {
    el.style.animation = 'none';
    el.style.opacity = '0.95';
    const [x, y, face] = places[i % places.length];
    const flip = face < 0 ? ' scaleX(-1)' : '';
    el.style.transform = `translate(${x}vw, ${y}vh) rotate(${face*6}deg)${flip}`;
  });
  return bats.length;
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
        await page.wait_for_timeout(600)
        n = await page.evaluate(FORCE_MID)
        report.append(f"desktop forced bats: {n}")
        await page.wait_for_timeout(150)
        await page.screenshot(path=str(OUT / "bats-d1280-midflight.png"), full_page=False)

        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(250)
        await page.fill('#f-name', 'Bat Test')
        await page.fill('#f-phone', '4078639276')
        await page.fill('#f-email', 'bat-test@example.com')
        await page.check('#f-consent')
        await page.click('#submit')
        await page.wait_for_timeout(950)
        deliv = await page.evaluate("""() => {
          const d = document.querySelector('.dbat');
          if (!d) return null;
          const r = d.getBoundingClientRect();
          return {left:r.left, top:r.top, w:r.width, cls:d.className};
        }""")
        report.append(f"desktop delivery: {deliv}")
        await page.screenshot(path=str(OUT / "bats-d1280-delivery.png"), full_page=False)
        await ctx.close()

        ctx = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2, is_mobile=True, has_touch=True,
        )
        page = await ctx.new_page()
        await page.emulate_media(reduced_motion="no-preference")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(500)
        n = await page.evaluate(FORCE_MID)
        pe = await page.evaluate("() => getComputedStyle(document.getElementById('bat-layer')).pointerEvents")
        report.append(f"phone forced bats: {n} pe={pe}")
        await page.wait_for_timeout(150)
        await page.screenshot(path=str(OUT / "bats-p390-midflight.png"), full_page=False)

        await page.evaluate("document.getElementById('claim').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(250)
        await page.fill('#f-name', 'Bat Phone')
        await page.fill('#f-phone', '4078639276')
        await page.fill('#f-email', 'bat-phone@example.com')
        await page.check('#f-consent')
        await page.click('#submit')
        await page.wait_for_timeout(950)
        await page.screenshot(path=str(OUT / "bats-p390-delivery.png"), full_page=False)
        await ctx.close()
        await browser.close()
    print("\n".join(report))

asyncio.run(main())
