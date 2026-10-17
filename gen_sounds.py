# Generates the game's sound effects (own arcade-style designs, not copies of any recording).
import numpy as np, wave, os
SR = 22050
OUT = 'sounds'

def tri(phase):  return 2 * np.abs(2 * ((phase / (2*np.pi)) % 1) - 1) - 1
def sq(phase, duty=0.5): return np.where(((phase / (2*np.pi)) % 1) < duty, 1.0, -1.0)
def phase_of(freq):  return 2 * np.pi * np.cumsum(freq) / SR

def loopable(freq):
    """scale a frequency curve slightly so the loop ends on a whole number of cycles (no click)"""
    cycles = np.sum(freq) / SR
    return freq * (round(cycles) / cycles)

def save(name, x, vol=0.5):
    x = np.clip(x * vol, -1, 1)
    data = (x * 32767).astype('<i2').tobytes()
    with wave.open(os.path.join(OUT, name), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)
    print(f'{name:16s} {len(x)/SR:5.2f} s')

def env(n, attack=0.004, release=0.02):
    e = np.ones(n); a = int(attack*SR); r = int(release*SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] = np.linspace(1, 0, r)
    return e

t = lambda d: np.arange(int(d * SR)) / SR

# chomp: two halves of a "waka" - a quick falling and a quick rising sweep
for name, f0, f1 in (('chomp_a.wav', 560, 240), ('chomp_b.wav', 240, 560)):
    n = int(0.105 * SR); f = np.linspace(f0, f1, n)
    save(name, tri(phase_of(f)) * env(n, 0.002, 0.03), 0.55)

# siren loops: rising and falling tone, faster and higher as the maze empties
for name, dur, lo, hi in (('siren_1.wav', 0.44, 380, 620), ('siren_2.wav', 0.36, 430, 720), ('siren_3.wav', 0.28, 480, 820)):
    n = int(dur * SR); x = np.linspace(0, 1, n, endpoint=False)
    shape = 0.5 - 0.5 * np.cos(2 * np.pi * x)
    f = loopable(lo + (hi - lo) * shape)
    save(name, 0.7 * tri(phase_of(f)) + 0.3 * np.sin(phase_of(f)), 0.32)

# fright loop: low buzzing wobble
n = int(0.27 * SR); x = np.linspace(0, 1, n, endpoint=False)
f = loopable(170 + 160 * ((x * 3) % 1))
save('fright.wav', sq(phase_of(f), 0.4), 0.18)

# eyes loop: fast high warble
n = int(0.17 * SR); x = np.linspace(0, 1, n, endpoint=False)
f = loopable(800 + 900 * ((x * 2) % 1) ** 0.7)
save('eyes.wav', sq(phase_of(f), 0.5), 0.14)

# eat ghost: fast rising sweep
n = int(0.48 * SR); x = np.linspace(0, 1, n)
f = 180 * (1700 / 180) ** x
save('eat_ghost.wav', sq(phase_of(f), 0.5) * env(n, 0.003, 0.08), 0.25)

# eat fruit: two short upward chirps
parts = []
for f0, f1 in ((500, 1100), (700, 1500)):
    n = int(0.12 * SR); f = np.linspace(f0, f1, n)
    parts += [tri(phase_of(f)) * env(n, 0.002, 0.02), np.zeros(int(0.04 * SR))]
save('eat_fruit.wav', np.concatenate(parts), 0.55)

# death: a falling series of warbles, then two low pops
parts = []
for k in range(9):
    n = int(0.11 * SR); x = np.linspace(0, 1, n)
    top = 900 - k * 70
    f = top - (top * 0.55) * x + 60 * np.sin(2 * np.pi * 3 * x)
    parts.append(tri(phase_of(f)) * env(n, 0.003, 0.02))
parts.append(np.zeros(int(0.12 * SR)))
for _ in range(2):
    n = int(0.09 * SR); f = np.linspace(260, 60, n)
    parts += [sq(phase_of(f)) * env(n, 0.001, 0.04) * 0.8, np.zeros(int(0.07 * SR))]
save('death.wav', np.concatenate(parts), 0.45)

# start: an original 2-second jingle (melody + bass), not the arcade tune
def note(freq, dur, wave_fn, duty=0.5, gap=0.012):
    n = int(dur * SR); m = n - int(gap * SR)
    out = np.zeros(n)
    if freq:
        ph = 2 * np.pi * freq * np.arange(m) / SR
        out[:m] = (wave_fn(ph) if wave_fn is not sq else sq(ph, duty)) * env(m, 0.003, 0.03)
    return out
N = lambda s: 440 * 2 ** ((s - 69) / 12)   # MIDI note -> Hz
step = 0.125
melody = [72, 76, 79, 84, 83, 79, 76, 79, 81, 77, 74, 77, 79, 76, 72, None]
bass   = [48, 55, 52, 55, 47, 55, 52, 55, 53, 57, 50, 57, 55, 52, 48, None]
mel = np.concatenate([note(N(m) if m else 0, step, sq, 0.25) for m in melody])
bas = np.concatenate([note(N(b) if b else 0, step, tri) for b in bass])
save('start.wav', 0.55 * mel + 0.6 * bas, 0.5)
