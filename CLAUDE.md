# Bjeshka – project memory for Claude Code

> The owner writes in Albanian (Kosovo dialect). Reply in Albanian; keep code, comments and commits in English.

## What this is
**Bjeshka** ("the highlands") is a 2D side-scrolling **mountain-bike game set in Kosovo**, made in a silhouette style
like *Mountain Bike Xtreme*: layered misty forests, a rider in silhouette, and four round on-screen buttons.
It is a single-file HTML5 canvas game, wrapped as an **Android app** (a Kotlin WebView). The game itself is
`app/src/main/assets/game/index.html`, with no build step and no libraries. The same file runs in a browser and is also
published as a claude.ai artifact.

The owner also builds other games: *Shqiptari* (a platformer for the LG Content Store) and *Pishpirik* (a card game with a webOS TV app).
He has an Android app `al.market.stoku`, and this app follows that package-name style: **`al.bjeshka.game`**.

## Repo layout
```
.github/workflows/build-apk.yml   CI: builds debug APK on every push (artifact "Bjeshka-debug-apk");
                                  signed release APK+AAB if secrets KEYSTORE_BASE64, KEYSTORE_PASSWORD, KEY_ALIAS, KEY_PASSWORD exist
app/src/main/java/al/bjeshka/game/MainActivity.kt   full-screen WebView, WebViewAssetLoader, back button, pause/resume
app/src/main/assets/game/index.html                  THE GAME (≈900 lines, sections marked /* ===== name ===== */)
app/src/main/assets/game/sounds/*.mp3                real nature recordings (see sounds/CREDITS.md)
app/src/main/res/drawable/ic_launcher_*.xml          adaptive icon (vector): rider in front of dusk mountains
tools/test_levels.js      node+playwright: bot plays all 10 levels headless. `full` bot (pedal+lean+brake) must FINISH, `pedal`-only bot must NOT.
                          Run after ANY physics/terrain change:  NODE_PATH=$(npm root -g) node tools/test_levels.js
tools/drop_test.js        landing feel: drops the bike from 20-320 px, prints suspension travel used and peak load in g
tools/screenshots.js      every level at several camera positions → tools/shots/  (node tools/screenshots.js [lv] [camX,camX])
tools/build_sounds.py     rebuild sounds/ from the Moodist repo
```
No `gradlew` or wrapper jar is committed; CI uses `gradle/actions/setup-gradle` with Gradle 8.13. To add the wrapper locally, run
`gradle wrapper --gradle-version 8.13`. Versions in use: AGP 8.13.0, Kotlin 2.2.20, compileSdk/targetSdk 36, minSdk 26, Java 17, `androidx.webkit:webkit:1.14.0`.

## Android wrapper (MainActivity.kt)
- Serves assets at `https://appassets.androidplatform.net/assets/game/index.html`, so `fetch('sounds/x.mp3')` works. `file://` would block it.
- The orientation is `sensorLandscape`, the screen is immersive full-screen, `FLAG_KEEP_SCREEN_ON` is set, and the cutout mode is shortEdges.
- The user agent gets the suffix `BjeshkaApp/1.0`. The game hides its "Ekran i plotë" (fullscreen) button when it sees this.
- JS bridge functions defined in index.html:
  - `androidBack()` returns `'ok'` or `'exit'`. In a level it toggles pause, on the results screen it goes to the menu, and in the menu it exits.
  - `androidPause()` and `androidResume()` are called from onPause and onResume.
- Progress is saved in `localStorage` under key `bjeshka_v1` = `{u: unlockedCount, best:{lv:{t,s,f}}, snd}`. `domStorageEnabled=true` is required for this.

## Game architecture (index.html sections)
- **constants**: `SEG=8` px terrain sample, `R=13` wheel radius, `WB=44` wheelbase, `GRAV=560`, `ACC=330`, `MAXV=300`,
  `PXM=40` px per metre, `DT=1/240` fixed physics step.
  - The owner asked for a **slower** bike, so speed was reduced from 440 to 300 (about 27 km/h). Don't make it faster without asking.
- **levels**: the `LEVELS[]` array (index 0–9). Fields:
  - name `n`, place `p`, time of day `tm` ∈ day|dawn|dusk|eve|night
  - weather `w` ∈ clear|fog|rain|snow|storm|blizzard
  - `sky[2]`, `fog`, `gr` (ground) colours: every silhouette layer is a mix of `fog` and `gr`
  - landmark `land` ∈ prishtina|waterfall|kulla|fortress|peaks|ski|village
  - flags `snow`, `light` (headlight at night), `birds`, `cuckoo`, `crickets`, `owl`, `flies` (fireflies)
  1. Gërmia (Prishtinë) – day
  2. Mirusha – dawn, fog, waterfall
  3. Rugova – rain, kulla towers
  4. Prizreni – dusk, fortress
  5. Bjeshkët e Nemuna – clear night
  6. Brezovica – snow, ski lift
  7. Drenica – evening rain (teal palette, like the reference screenshot)
  8. Gjeravica – storm with lightning
  9. Sharri – night blizzard
  10. Rugova natën – night storm
- **terrain**: `genTerrain(n)` is seeded and deterministic per level. Features: rolling hills, kickers (the ramp lip angle is capped at about 34°,
  `lr = hr*3`), pits/gaps from level 4 (width `56+d*42+rng*14`; must stay jumpable at MAXV), step-ups, rock gardens
  (smooth `sin²` bumps ≤ 8 px), steep descents. Levels are **2x** the original length (`len=(9000+n*1500)*2`).
  - **Control hazards** (`haz[]`): every ~2300-3800 px a steep plunge (>=52 deg, 170-260 px long) or from level 3 a drop-off cliff (210-320 px). Pedalling alone crashes on both;
    the player must lean back (and may brake). Each is followed by a gentle climb that recovers ~75% of the height. The owner asked that no level can be finished by holding only the pedal button.
    Checkpoints are kept out of hazard zones. Also produces checkpoints `cps` every 1400 px, kept at least 650 px before a pit, and `finish`.
  - Past bugs that were fixed: pits were 1200 px deep because the second `seg()` call was relative; 60° ramps stalled the bike;
    sharp rocks trapped the wheel.
- **physics**: three Verlet points: rear wheel, front wheel, rider/frame mass `H` (im 1.15/1.15/0.9).
  - The wheelbase is rigid.
  - The rider hangs on **two spring-dampers** (rear shock and fork): `SK=170, SCC=11 (compression), SCR=24 (rebound), STRAVEL=22, SEXT=4, SPROG=5` (progressive spring = soft bump-stop).
    A 1.5 m drop uses ~65% travel at ~5 g (it used to bottom out at 18 g, "like a rock"). Landing feedback in `landFx()`: camera dip, dust, softer thud; the rider crouches deeper with compression (`comp`). Check with `tools/drop_test.js`.
  - Drive and brakes act on the **whole bike** (`dv` applied to all points along the ground tangent), not only the tyre. Previously, mass ratios made the bike sluggish.
  - Aerodynamic drag: `b.drag`.
  - Lean torque is applied around the centroid: 16 rad/s² in the air, 9 on the ground.
  - Crash when the head point touches the ground, falls into a pit, or drops far below the terrain. Respawn at the last checkpoint after 1.4 s.
  - Holding brake at a standstill rolls the bike backwards, to get unstuck.
  - Flips are counted from accumulated air rotation (toast "Salto!").
- **scenery** (real places, researched): `rockWall` (Rugova gorge: sheer grey limestone walls, ledge pines, caves; Mirusha canyon), `crags` (jagged snow-capped alpine peaks; Gjeravica has one dominant pyramid),
  `hillTown` (Prizren: Kalaja fortress on a crag, Nenkalaja old town of white houses with terracotta roofs climbing the slope, minarets, Sinan Pasha-style mosque, Stone Bridge, Sharr peaks behind),
  Brezovica ski trails + lift + hotel, Drenica farmland patchwork + stone houses + kullas, Prishtina skyline with the Mother Teresa cathedral, stan huts in the Bjeshket e Nemuna. Level 3 and 10 use `land:'rugova'`.
- **rendering**:
  - Sky with sun, moon and stars, clouds, lightning bolt.
  - Five parallax layers pre-rendered to tile canvases (`buildLayers`): mountains with snow caps, hills with landmarks, pines, mixed forest,
    tall trunks like the reference.
  - World decor trees and haystacks (mullar), terrain with grass or a snow strip, dirt/mud/snow spray from the rear tyre.
  - Realistic enduro bike: knobby tyres, 28 spokes, disc rotors, fork stanchions, rear shock, chain.
  - Rider with real proportions: full-face helmet, hydration pack, IK legs on rotating cranks, IK arms, cranks settle level when coasting.
  - The owner rejected the first "cartoonish" stick figure, so keep the realistic proportions.
  - Weather particles; fireflies and headlight cone at night.
- **audio (`AU`)**:
  - Real recordings: `LOOPS` (seamless loops with 0.5 s padding, played with loopStart and loopEnd) and `SHOTS` (one-off events).
  - Per-level mix in `ENV[]`; each level loads only the files it needs, to save phone memory.
  - Thunder is delayed after lightning by distance, and lowpassed when far away.
  - The waterfall is spatial: it is audible and panned only while the waterfall is on screen.
  - The wind loop is lowpassed and rises with speed (air rush).
  - Synthesized fallbacks exist for everything (rain drops, birds, crickets, owl, cuckoo, thunder). Tyre noise, freewheel clicks, the landing thud
    and UI sounds are synthesized.
  - **Logic rules the owner asked for:**
    - No birds (visual flock or sound) unless the weather is clear or fog and it is not night or evening.
    - The cuckoo also only sings in clear or fog weather.
    - No river or waterfall loops in dry levels: they sound like rain. This was a reported bug in Prizren.
- **UI**:
  - All Albanian text.
  - **No emoji anywhere.** Icons are inline SVG:
    - `IC.*` primitives and `LVART[]` per-level card art drawn over the level's own sky and ridges by `cardArt()`
    - `UI.*` button icons, stars, the checkered flag, and the Kosovo flag
  - HUD: time, metres, flips, progress bar between checkpoints.
  - Buttons: lean back, lean forward, brake, pedal. Pointer events support multi-touch.
  - Keyboard: arrows or WASD, Space to pedal, P to pause, R to restart.

## Conventions / gotchas
- Edit the game only in `app/src/main/assets/game/index.html`. Keep it a single file with inline CSS and JS.
- After changing physics or terrain, run `node tools/test_levels.js` (needs `npm i -g playwright`). Every line must print OK: the full bot finishes all 10 levels with 0 crashes and the pedal-only bot never finishes.
- Wrap `localStorage` in try/catch, because it can throw.
- Everything is tuned for phone landscape (844×390). `ZOOM = min(H/250, W/430)`.
- Sound licences: Pixabay Content License or CC0, via Moodist. Keep `sounds/CREDITS.md` and the credit line in the menu.

## Ideas / not done yet
- Real recordings for the cuckoo, bike tyres on gravel and the freewheel (currently synthesized).
- More levels, such as Kaçanik gorge, Llapi, Shkugëza or Prevalla. A leaderboard (Firebase, like Pishpirik). Haptics on landing through a JS bridge.
- Play Store listing assets: feature graphic and screenshots (`tools/screenshots.py` helps).
- webOS / LG TV build, like his other games. It would need d-pad controls.
