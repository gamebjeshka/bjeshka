// Landing feel test: drops the bike flat from several heights, reports suspension use and peak load.
const path = require('path'); const { chromium } = require('playwright');
const GAME = 'file://' + path.resolve(__dirname, '../app/src/main/assets/game/index.html');
const JS = (h) => {
  startLevel(0); state = 'x'; const x = 600; bike = makeBike(x);
  for (const q of bike.p) { q.y -= h; q.py = q.y; }
  ctrl.pedal = false; ctrl.back = ctrl.fwd = ctrl.brake = false;
  let maxC = 0, peak = 0, pvy = 0, t = 0, landT = -1, hy0 = bike.p[2].y, minHy = 1e9, maxHy = -1e9, bounces = 0, lastDir = 0, crashed = false;
  for (let s = 0; s < 240 * 3; s++) {
    physStep(); t += DT;
    const q = bike.p, dR = Math.hypot(q[2].x - q[0].x, q[2].y - q[0].y), dF = Math.hypot(q[2].x - q[1].x, q[2].y - q[1].y);
    const cR = (bike.cons[1][2] - dR) / STRAVEL, cF = (bike.cons[2][2] - dF) / STRAVEL; maxC = Math.max(maxC, cR, cF);
    const vy = (q[2].y - q[2].py) / DT; const ay = (vy - pvy) / DT; pvy = vy; if (landT < 0 && (bike.contact[0] || bike.contact[1])) landT = t;
    if (landT >= 0 && Math.abs(ay) > peak) peak = Math.abs(ay);
    if (!game.alive) crashed = true;
  }
  return { drop: h, travelUsed: +maxC.toFixed(2), peakAccelG: +(peak / GRAV).toFixed(1), crashed, settledVy: +((bike.p[2].y - bike.p[2].py) / DT).toFixed(1) };
};
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 844, height: 390 } });
  await pg.goto(GAME); await pg.waitForTimeout(300);
  for (const h of [20, 60, 120, 200, 320]) console.log(JSON.stringify(await pg.evaluate(JS, h)));
  await b.close(); })();
