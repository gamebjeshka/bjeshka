"""Screenshots of the menu and every level (phone landscape 844x390) into tools/shots/.
Usage: python tools/screenshots.py"""
import asyncio, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent
GAME = (ROOT.parent / 'app/src/main/assets/game/index.html').as_uri()
async def main():
    (ROOT / 'shots').mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 844, 'height': 390})
        await pg.goto(GAME); await pg.wait_for_timeout(600)
        await pg.screenshot(path=str(ROOT / 'shots/menu.png'))
        for lv in range(10):
            await pg.evaluate(f'startLevel({lv});ctrl.pedal=true'); await pg.wait_for_timeout(3000)
            await pg.screenshot(path=str(ROOT / f'shots/level{lv+1}.png'))
            await pg.evaluate('ctrl.pedal=false')
        await b.close()
asyncio.run(main())
