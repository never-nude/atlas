#!/usr/bin/env python3
"""worldbook_claude build — polish step 1: thin the flow ribbons + lower the lift.

Codex's lifted-3D arcs are thick, densely stacked, and high-lift: dramatic but busy.
dots_pop.py already made the moving nodes prominent. This makes the ribbons the *guides*
and the nodes the *star*:

  1) ribbon half-width  -> ~0.58x  (thinner corridors)
  2) lift base + peak   -> ~0.65x  (calmer altitude)

The lift is deliberately only lowered, NOT removed: lifted 3D arcs are the ONLY durable fix
for the polar/Arctic ring artifact on near-antipodal pairs (US<->India apex ~84N). At 0.65x
the long-arc apex is still ~870km of altitude — plenty of surface clearance, no rings.

Idempotent. Usage:  python3 ribbons_thin_lift_lower.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    # 1) ribbon half-width in the flow-3d LINE vertex shader (~0.58x)
    (
        "ribbon width",
        "float zt=clamp((u_zoom-1.5)/7.5,0.0,1.0), px=mix(mix(2.0,4.6,a_w),mix(6.0,13.8,a_w),zt);",
        "float zt=clamp((u_zoom-1.5)/7.5,0.0,1.0), px=mix(mix(1.2,2.7,a_w),mix(3.4,7.6,a_w),zt);",
    ),
    # 2a) lift base (~0.63x) — keeps a low floor so short arcs sit just off the surface
    (
        "lift base",
        "const base=pathMode?32000:95000;",
        "const base=pathMode?21000:60000;",
    ),
    # 2b) lift peak (~0.66x) — calmer apex, still high enough to defeat ring artifacts
    (
        "lift peak",
        "const peak=pathMode?(140000+260000*far):(440000+900000*far);",
        "const peak=pathMode?(92000+172000*far):(290000+595000*far);",
    ),
]

results = []
for name, old, new in EDITS:
    if new in text:
        results.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new)
        results.append((name, "patched"))
    else:
        results.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = all(s in ("patched", "already-applied") for _, s in results)
for name, s in results:
    print(f"  [{s:>16}] {name}")
print("OK: ribbons thinned + lift lowered" if ok else "WARN: an anchor was not found — check the build version")
sys.exit(0 if ok else 1)
