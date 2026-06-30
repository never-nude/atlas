#!/usr/bin/env python3
"""worldbook_claude build — make path SOURCES visible + make arcs tappable on mobile.

Two fixes:
  1) The per-layer Source citation was rendering but sat below the fold of a short,
     scrollable legend (max-height 240px desktop / 30vh mobile). Raise the cap so the
     citation shows without scrolling. (overflow-y:auto stays as a safety net.)
  2) Flow arcs are hard to tap, especially on mobile: the click/hover hit-test uses the
     invisible "flow-lines" surface layer, only ~2.4-5.6px wide on mobile. Widen that
     INVISIBLE hit line (the visible art is the separate WebGL layer, so this changes the
     tap target only, not the look).

Idempotent. Usage:  python3 legend_and_tap.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    # 1) widen the invisible hit-test line so arcs are easy to tap (mobile especially)
    (
        "tap target (hit-line width)",
        "  const wlo=m?2.4:2.0, whi=m?5.6:4.6, rlo=m?2.2:1.8, rhi=m?4.4:3.4;",
        "  const wlo=m?7.0:3.0, whi=m?13.0:6.5, rlo=m?2.2:1.8, rhi=m?4.4:3.4;",
        "const wlo=m?7.0:3.0",
    ),
    # 2a) desktop legend: taller so the Source citation is visible without scrolling
    (
        "legend height (desktop)",
        "max-width:240px;max-height:240px;overflow-y:auto",
        "max-width:240px;max-height:64vh;overflow-y:auto",
        "max-width:240px;max-height:64vh",
    ),
    # 2b) mobile legend: taller too
    (
        "legend height (mobile)",
        "max-width:58vw;max-height:30vh;",
        "max-width:58vw;max-height:52vh;",
        "max-width:58vw;max-height:52vh;",
    ),
]

results = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        results.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1)
        results.append((name, "patched"))
    else:
        results.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = all(s in ("patched", "already-applied") for _, s in results)
for name, s in results:
    print(f"  [{s:>16}] {name}")
print("OK: sources visible + arcs tappable" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
