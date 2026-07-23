import sys
sys.path.insert(0, "src")

from harmonyforge.ai.prompt_parser import extract_structured_params

tests = [
    ("dark travis x metro f# 8 bars",               ["metro_boomin"], ["travis_scott"], "F#",  "minor",         None,  8),
    ("ATL x Tay Keith phrygian d 163 bpm drill",    ["atl_jacob","tay_keith"], [],      "D",   "phrygian",      163,   8),
    ("emotional neo-soul mike dean c dorian 16 bars",["mike_dean"], [],          "C",   "dorian",        None, 16),
    ("southside x metro evil bb minor 140 bpm",     ["southside","metro_boomin"],[],    "Bb",  "minor",         140,   8),
    ("make me something dark bouncy metro f# harmonic",["metro_boomin"],[],     "F#",  "harmonic_minor",None,   8),
]

all_pass = True
for query, exp_prod, exp_art, exp_key, exp_scale, exp_bpm, exp_bars in tests:
    p = extract_structured_params(query)
    ok_prod  = sorted(p["producers"]) == sorted(exp_prod)
    ok_art   = sorted(p["artists"])   == sorted(exp_art)
    ok_key   = p["key"]   == exp_key
    ok_scale = p["scale"] == exp_scale
    ok_bpm   = p["bpm"]   == exp_bpm
    ok_bars  = p["bars"]  == exp_bars
    passed   = all([ok_prod, ok_art, ok_key, ok_scale, ok_bpm, ok_bars])
    status   = "PASS" if passed else "FAIL"
    if not passed:
        all_pass = False
    print(f"[{status}] {query!r}")
    if not ok_prod:  print(f"       prod:  got {p['producers']} expected {exp_prod}")
    if not ok_art:   print(f"       art:   got {p['artists']}   expected {exp_art}")
    if not ok_key:   print(f"       key:   got {p['key']}       expected {exp_key}")
    if not ok_scale: print(f"       scale: got {p['scale']}     expected {exp_scale}")
    if not ok_bpm:   print(f"       bpm:   got {p['bpm']}       expected {exp_bpm}")
    if not ok_bars:  print(f"       bars:  got {p['bars']}      expected {exp_bars}")

print()
print("ALL PASS" if all_pass else "SOME FAILED")
