// Headless bot playthrough (node + playwright).  Usage: node tools/test_levels.js [lv|all]
// Modes per level:  full  = pedal + lean to slope + brake on steep descents (must FINISH)
//                   pedal = ONLY the pedal button, nothing else            (must NOT finish: levels need leaning/braking)
const path = require('path');
const { chromium } = require('playwright');
const GAME = 'file://' + path.resolve(__dirname, '../app/src/main/assets/game/index.html');
const JS = ({ lv, mode }) => {
  startLevel(lv); state = 'x'; let steps = 0; const maxS = 240 * 900, maxCrash = 40;
  while (steps < maxS && game.crashes < maxCrash) {
    const p = bike.p, a = Math.atan2(p[1].y - p[0].y, p[1].x - p[0].x), mx = (p[0].x + p[1].x) / 2;
    const sl = Math.atan2(Hx(mx + 30) - Hx(mx - 10), 40), air = !bike.contact[0] && !bike.contact[1];
    ctrl.pedal = true; ctrl.back = false; ctrl.fwd = false; ctrl.brake = false;
    if (mode === 'full') {
      const tgt = air ? Math.atan2(Hx(mx + 60) - Hx(mx + 20), 40) : sl;
      if (a - tgt > .12) ctrl.back = true; else if (a - tgt < -.12) ctrl.fwd = true;
      const v = (p[0].x - p[0].px) / DT;
      if (!air && sl > .6 && v > 340) { ctrl.brake = true; ctrl.pedal = false }   // steep plunge: brake
    }
    physStep(); steps++; game.time += DT;
    if (!game.alive) { game.crashT -= DT; if (game.crashT <= 0) respawn() }
    while (game.cp + 1 < T.cps.length && mx > T.cps[game.cp + 1]) game.cp++;
    if (p[0].x > T.finish) break;
  }
  for (const k in ctrl) ctrl[k] = false;
  return { lv, mode, done: bike.p[0].x > T.finish, seconds: Math.round(steps / 240), crashes: game.crashes, len: Math.round(T.finish) };
};
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 844, height: 390 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(GAME); await pg.waitForTimeout(300);
  const arg = process.argv[2] || 'all', modes = (process.argv[3] || 'full,pedal').split(',');
  const lvls = arg === 'all' ? [...Array(10).keys()] : [+arg];
  let bad = 0;
  for (const lv of lvls) for (const mode of modes) {
    const r = await pg.evaluate(JS, { lv, mode }); const ok = mode === 'full' ? r.done : !r.done; if (!ok) bad++;
    console.log(ok ? 'OK  ' : 'FAIL', JSON.stringify(r));
  }
  console.log('page errors:', errs, ' failures:', bad); await b.close(); process.exit(bad ? 1 : 0);
})();
