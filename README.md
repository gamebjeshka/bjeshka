# Bjeshka – Android app

## APK direkt nga GitHub (pa Android Studio)
1. Ngarko krejt këto skedarë në repo (dosja `.github` duhet me qenë në rrënjë).
2. Te repo → **Actions** → "Build APK" nis vetë pas çdo push-i (ose shtyp **Run workflow**).
3. Kur përfundon (~5 min) → hape run-in → poshtë te **Artifacts** → shkarko **Bjeshka-debug-apk** → instaloje në telefon.

**APK/AAB i nënshkruar për Play Store:** te repo → Settings → Secrets and variables → Actions, shto:
`KEYSTORE_BASE64` (keystore-i i koduar me `base64 -w0 release.jks`), `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`.
Atëherë workflow-i krijon edhe **Bjeshka-release** (.apk + .aab).

`CLAUDE.md` = memoria e projektit për Claude Code (lexohet automatikisht kur hap session në këtë repo).

The game (HTML5) lives in `app/src/main/assets/game/` and runs inside a full-screen WebView.

## Hapat në Android Studio
1. **File → Open** → zgjidh dosjen `Bjeshka`.
2. Prit **Gradle Sync** (herën e parë shkarkon Gradle 8.13 dhe Android plugin – duhet internet).
   Nëse Studio të ofron "Upgrade Android Gradle Plugin", mund ta pranosh.
3. Lidhe telefonin (USB debugging) ose hap një emulator → **Run ▶**.

## APK / AAB për Play Store
- **Build → Generate Signed App Bundle / APK** → krijo një keystore (ruaje mirë, pa të s'mund ta përditësosh app-in) → *release*.
- Për Google Play përdor **.aab**; për ta instaluar direkt në telefon përdor **.apk**.

## Përditësimi i lojës
Zëvendëso `app/src/main/assets/game/index.html` (dhe dosjen `sounds/`) me versionin e ri,
rrite `versionCode` te `app/build.gradle.kts`, pastaj bëj build përsëri.

## Çka bën app-i
- Ekran i plotë, horizontal, ekrani nuk fiket gjatë lojës.
- Butoni **Back**: në lojë = pauzë/vazhdo, te rezultati = menyja, në menu = del nga app-i.
- Kur del nga app-i ose vjen thirrje, loja pauzohet dhe zëri ndalet.
- Progresi (nivelet e hapura, kohët) ruhet në telefon.
- Package: `al.bjeshka.game` (ndryshoje te `app/build.gradle.kts` nëse do tjetër).

Zërat e natyrës: inçizime reale (CC0 / Pixabay Content License) nga projekti open-source Moodist.
