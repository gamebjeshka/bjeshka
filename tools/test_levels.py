"""Bot playthrough of all 10 levels (headless Chrome via Playwright).
Usage:  pip install playwright && playwright install chromium
        python tools/test_levels.py
Each level must print done=True. The bot pedals constantly and leans to match the slope."""
import asyncio, pathlib
from playwright.async_api import async_playwright
GAME = (pathlib.Path(__file__).resolve().parent.parent / 'app/src/main/assets/game/index.html').as_uri()
JS = '''(lv)=>{startLevel(lv);state='x';let steps=0;const maxS=240*400;
while(steps<maxS){const p=bike.p;const a=Math.atan2(p[1].y-p[0].y,p[1].x-p[0].x);const mx=(p[0].x+p[1].x)/2;
 const sl=Math.atan2(Hx(mx+30)-Hx(mx-10),40);const air=!bike.contact[0]&&!bike.contact[1];
 ctrl.pedal=true;ctrl.back=false;ctrl.fwd=false;const tgt=air?Math.atan2(Hx(mx+60)-Hx(mx+20),40):sl;
 if(a-tgt>0.12)ctrl.back=true; else if(a-tgt<-0.12)ctrl.fwd=true;
 physStep();steps++;game.time+=DT;
 if(!game.alive){game.crashT-=DT;if(game.crashT<=0)respawn()}
 while(game.cp+1<T.cps.length&&mx>T.cps[game.cp+1])game.cp++;
 if(p[0].x>T.finish)break;}
for(const k in ctrl)ctrl[k]=false;
return {lv,done:bike.p[0].x>T.finish,seconds:Math.round(steps/240),crashes:game.crashes}}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 844, 'height': 390})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(GAME); await pg.wait_for_timeout(300)
        for lv in range(10):
            print(await pg.evaluate(JS, lv))
        print('page errors:', errs)
        await b.close()
asyncio.run(main())
