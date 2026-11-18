// Screenshots of levels at several camera positions -> tools/shots/  (node tools/screenshots.js [lv|all] [camX,camX,...])
const path = require('path'), fs = require('fs'); const { chromium } = require('playwright');
const GAME = 'file://' + path.resolve(__dirname, '../app/src/main/assets/game/index.html');
(async () => {
  const out = path.resolve(__dirname, 'shots'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 844, height: 390 } });
  await pg.goto(GAME); await pg.waitForTimeout(400);
  const arg = process.argv[2] || 'all', xs = (process.argv[3] || '300,4200,8200').split(',').map(Number);
  for (const lv of arg === 'all' ? [...Array(10).keys()] : [+arg]) for (const x of xs) {
    await pg.evaluate(({ lv, x }) => { startLevel(lv); state = 'x'; bike = makeBike(x - 110); cam.x = x; cam.y = Hx(x) - 22; cam.ys = cam.y; cam.k = cam.kv = 0; for (let i = 0; i < 40; i++)physStep(); document.querySelectorAll('#hud,#ctl,#toast').forEach(e => e.style.display = 'none'); render(1, 0); }, { lv, x });
    await pg.screenshot({ path: path.join(out, `lv${lv + 1}_${x}.png`) });
  }
  await b.close();
})();
