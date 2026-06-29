#!/usr/bin/env python3
"""worldbook_claude build — backlog #1 (debt), follow-up: DEMARCATE no-data countries.

Flat gray alone can't be told apart from the pale/low end of a color ramp (cream "little owed"
~ gray "no data"). The cartographically correct fix is TEXTURE, which is orthogonal to color:
no-data countries get a diagonal HATCH so they're unmistakable on every debt view regardless
of the ramp.

What this adds (debt views only — govdebt / debtout / debtin):
  - a generated diagonal-stripe image "nodata-hatch"
  - a "nodata-hatch" fill layer (above fills, below borders) on the world source
  - updateNoDataHatch(key): filters the hatch to countries lacking the active layer's data
    property and shows it only for the three debt views; hidden everywhere else
  - wiring in setFlowBase (flow path: debtout/debtin) and setLayer (choropleth path: govdebt)

Idempotent. Usage:  python3 debt_nodata_hatch.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

# ---- EDIT A: add the hatch image + layer right after the borders layer ---------------------
A_OLD = (
    '  map.addLayer({id:"borders",type:"line",source:"world",\n'
    '    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});'
)
A_NEW = A_OLD + (
    '\n'
    '  (function(){\n'
    '    var HS=10, cv=document.createElement("canvas"); cv.width=cv.height=HS;\n'
    '    var cx=cv.getContext("2d"); cx.clearRect(0,0,HS,HS);\n'
    '    cx.strokeStyle="rgba(8,12,20,0.82)"; cx.lineWidth=2.4; cx.lineCap="round";\n'
    '    cx.beginPath(); cx.moveTo(0,HS); cx.lineTo(HS,0); cx.stroke();\n'
    '    var im=cx.getImageData(0,0,HS,HS);\n'
    '    if(map.hasImage&&!map.hasImage("nodata-hatch")) map.addImage("nodata-hatch",{width:HS,height:HS,data:new Uint8Array(im.data.buffer)});\n'
    '  })();\n'
    '  map.addLayer({id:"nodata-hatch",type:"fill",source:"world",\n'
    '    paint:{"fill-pattern":"nodata-hatch","fill-opacity":0,"fill-opacity-transition":{duration:300}},\n'
    '    filter:["==",["get","iso3"],"___none___"]}, "borders");'
)

# ---- EDIT B: define updateNoDataHatch() + call it at the top of setFlowBase -----------------
B_OLD = (
    'function setFlowBase(key){\n'
    '  if(subOn) return;'
)
B_NEW = (
    'function updateNoDataHatch(key){\n'
    '  if(!(map.getLayer && map.getLayer("nodata-hatch"))) return;\n'
    '  var f=FLOWS[key], prop=(f&&f.baseColorProp)?f.baseColorProp:("color_"+key);\n'
    '  var isDebt=(key==="govdebt"||key==="debtout"||key==="debtin");\n'
    '  if(isDebt && !subOn){ map.setFilter("nodata-hatch",["!",["has",prop]]); map.setPaintProperty("nodata-hatch","fill-opacity",0.9); }\n'
    '  else { map.setPaintProperty("nodata-hatch","fill-opacity",0); }\n'
    '}\n'
    'function setFlowBase(key){\n'
    '  if(subOn) return;\n'
    '  updateNoDataHatch(key);'
)

# ---- EDIT C: call updateNoDataHatch() in the choropleth path of setLayer --------------------
C_OLD = (
    '    map.setPaintProperty("sub-fills","fill-color",["coalesce",["get","color_"+key],noDataFor(key)]);\n'
    '  }\n'
    '  drawLegend(key);'
)
C_NEW = (
    '    map.setPaintProperty("sub-fills","fill-color",["coalesce",["get","color_"+key],noDataFor(key)]);\n'
    '  }\n'
    '  updateNoDataHatch(key);\n'
    '  drawLegend(key);'
)

EDITS = [
    ("hatch image + layer",       A_OLD, A_NEW, 'id:"nodata-hatch"'),
    ("updateNoDataHatch + wire flows", B_OLD, B_NEW, 'function updateNoDataHatch('),
    ("wire choropleth path",      C_OLD, C_NEW, 'updateNoDataHatch(key);\n  drawLegend(key);'),
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
print("OK: no-data countries demarcated with hatch (debt views)" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
