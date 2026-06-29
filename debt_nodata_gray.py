#!/usr/bin/env python3
"""worldbook_claude build — backlog #1 (debt recolor): clean separation of no-data vs data.

Intent (per Mike):
  - No-data countries must be a clear NEUTRAL GRAY, nowhere near the data color scheme.
  - The data palettes must NOT incorporate that gray at all — gray means "no data", period.

The debt DATA ramps are already saturated, gray-free hues (teal = lenders, brown->orange =
borrowers, green->red = govt debt). The problem is the *no-data* fill: today it's a dark
blue-slate ("#1a2433" on the follow-the-money flow views, "#262f3d" on the govt-debt
choropleth) that sits at nearly the same tone/hue family as the dark end of the data, so a
country with a little data blends into a country with none.

This swaps the no-data fill on the three debt views ONLY to a clearly lighter neutral gray
(no hue), so it can never be confused with teal/brown/green data. Other layers keep the
global NODATA slate.

Idempotent. Usage:  python3 debt_nodata_gray.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

DEBT_NODATA = "#4b4f55"  # balanced neutral gray (R~=G~=B), clearly lighter than the data darks

EDITS = [
    # 1) define the neutral-gray constant + a per-key fallback helper, right after NODATA
    (
        "DEBT_NODATA constant + helper",
        'const NODATA = "#262f3d";',
        'const NODATA = "#262f3d";\n'
        'const DEBT_NODATA = "' + DEBT_NODATA + '";\n'
        'function noDataFor(k){ return k==="govdebt" ? DEBT_NODATA : NODATA; }',
        'const DEBT_NODATA',           # idempotency sentinel
    ),
    # 2) route govt-debt choropleth no-data through the helper.
    #    This exact substring appears twice (colorExpr() + the sub-fills setter); both should
    #    use noDataFor(), so replace-all is intentional. Other layers use color_party /
    #    color_religion (different substrings) and are untouched.
    (
        "govt-debt choropleth fallback",
        '["coalesce",["get","color_"+key],NODATA]',
        '["coalesce",["get","color_"+key],noDataFor(key)]',
        '["coalesce",["get","color_"+key],noDataFor(key)]',
    ),
    # 3) follow-the-money flow base fill (debt-only: debtout/debtin are the only FLOWS with
    #    baseColorProp) -> neutral gray no-data.
    (
        "follow-the-money base fill",
        '["coalesce",["get",FLOWS[key].baseColorProp],"#3b4655"]',
        '["coalesce",["get",FLOWS[key].baseColorProp],DEBT_NODATA]',
        '["coalesce",["get",FLOWS[key].baseColorProp],DEBT_NODATA]',
    ),
]

results = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
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
print("OK: debt no-data = neutral gray, distinct from data" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
