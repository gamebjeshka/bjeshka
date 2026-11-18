"""Rebuild app/src/main/assets/game/sounds/ from the Moodist repo.
Usage: git clone --depth 1 https://github.com/remvze/moodist /tmp/moodist
       python tools/build_sounds.py /tmp/moodist/public/sounds
Needs ffmpeg + numpy. Loops are made seamless (equal-power crossfade) and padded with
0.5 s on both ends; the game plays them with loopStart=0.5, loopEnd=0.5+L (L = LOOPS in index.html)."""
import subprocess, sys, pathlib, numpy as np
SRC = pathlib.Path(sys.argv[1]); SR = 44100
OUT = pathlib.Path(__file__).resolve().parent.parent / 'app/src/main/assets/game/sounds'
def load(f):
    raw = subprocess.run(['ffmpeg','-v','error','-i',str(SRC/f),'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def save(a, name):
    a = np.clip(a, -1, 1).astype(np.float32)
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','libmp3lame','-b:a','64k',str(OUT/name)],input=a.tobytes(),check=True)
def norm(a, peak=.9, rms=None):
    if rms: a = a*(rms/(np.sqrt((a**2).mean())+1e-9))
    m = np.abs(a).max()
    return a*peak/m if m > peak else a
def loop(f, name, start, L, X=2.0, rms=.12):
    a = load(f); s = int(start*SR); n = int(L*SR); x = int(X*SR)
    seg = a[s:s+n+x].copy(); body = seg[:n].copy(); t = np.linspace(0,1,x)
    body[:x] = seg[:x]*np.sqrt(t) + seg[n:n+x]*np.sqrt(1-t)
    body = norm(body, rms=rms); M = int(.5*SR)
    save(np.concatenate([body[-M:], body, body[:M]]), name)
def clip(f, name, a0, a1, fade=.4, peak=.9):
    a = load(f)[int(a0*SR):int(a1*SR)].copy(); fi = int(.02*SR); fo = int(fade*SR)
    a[:fi] *= np.linspace(0,1,fi); a[-fo:] *= np.linspace(1,0,fo); save(norm(a, peak=peak), name)
OUT.mkdir(parents=True, exist_ok=True)
loop('animals/birds.mp3','birds.mp3',20,36); loop('animals/crickets.mp3','crickets.mp3',30,30)
loop('rain/light-rain.mp3','rain.mp3',30,30); loop('rain/heavy-rain.mp3','heavyrain.mp3',1,17,X=2.5)
loop('nature/wind.mp3','wind.mp3',10,32); loop('nature/howling-wind.mp3','howl.mp3',5,34)
loop('nature/waterfall.mp3','waterfall.mp3',1,18,X=2.5); loop('nature/river.mp3','river.mp3',20,30)
clip('rain/thunder.mp3','thunder1.mp3',0.3,18,fade=4,peak=.95); clip('rain/thunder.mp3','thunder2.mp3',20.8,38,fade=4,peak=.95)
clip('rain/thunder.mp3','thunder3.mp3',41.2,62,fade=5,peak=.95); clip('animals/owl.mp3','owl1.mp3',2.9,5.4,fade=.6,peak=.8)
clip('animals/owl.mp3','owl2.mp3',8.6,12.5,fade=.6,peak=.8); clip('animals/wolf.mp3','wolf.mp3',1.6,20,fade=3,peak=.8)
clip('animals/cows.mp3','cow1.mp3',9.2,11.4,fade=.5,peak=.8); clip('animals/cows.mp3','cow2.mp3',11.8,14.8,fade=.6,peak=.8)
clip('animals/crows.mp3','crows.mp3',12,22,fade=1.5,peak=.8); clip('animals/woodpecker.mp3','woodpecker.mp3',4.8,10,fade=.8,peak=.8)
clip('animals/dog-barking.mp3','dog.mp3',4.8,9.2,fade=.6,peak=.7); clip('animals/sheep.mp3','sheep.mp3',2,12,fade=1.5,peak=.7)
print('sounds written to', OUT)
