#!/usr/bin/env python3
"""Perf + path arcs + hover figures:
 1. PERF: the line-hover ran map.queryRenderedFeatures on EVERY fills mousemove (very expensive ->
    janky UI / sluggish layer switching). Replace with a cheap boolean flag.
 2. Dampen the PATH branch too (waypoint arcs); flatten centroid arcs a touch more (K 0.45->0.35).
 3. Hover shows a figure: plumb raw edge weight (wv) and display it.
python3 paths_and_figures.py index.html index.html   (idempotent)"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)

if 'let _onLine=false;' not in text:
    text=patch(text,'  const pop=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});',
        '  const pop=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});\n  let _onLine=false;','popdecl')
    text=patch(text,'    if(flowActive() && map.queryRenderedFeatures(e.point,{layers:["flow-lines"]}).length) return;',
        '    if(_onLine) return;','defer')
    text=patch(text,'  map.on("mousemove","flow-lines",e=>{ if(subOn||!flowActive()) return;',
        '  map.on("mousemove","flow-lines",e=>{ if(subOn||!flowActive()){ _onLine=false; return; } _onLine=true;','onmove')
    text=patch(text,'  map.on("mouseleave","flow-lines",()=>{ if(!subOn) map.getCanvas().style.cursor=""; });',
        '  map.on("mouseleave","flow-lines",()=>{ _onLine=false; if(!subOn) map.getCanvas().style.cursor=""; });','onleave')

if 'arcPoints(e.path[k]' not in text:
    text=patch(text,'gcPoints(e.path[k],e.path[k+1],14)','arcPoints(e.path[k],e.path[k+1],14)','path-dampen')
if 'var K=0.45;' in text:
    text=text.replace('var K=0.45;','var K=0.35;')

if ',nm:e.nm||null,amt:e.amt||null,wv:e.w}' not in text:
    text=text.replace(',nm:e.nm||null,amt:e.amt||null}',',nm:e.nm||null,amt:e.amt||null,wv:e.w}')
if 'p.wv!=null && p.wv' not in text:
    text=patch(text,'    const sub=p.amt || F.unit || F.label || "";',
      '    const sub = p.amt ? p.amt : (p.wv!=null && p.wv!=="" ? ((/billion|\\$/i.test(F.unit||"") ? ("\\u2248 $"+p.wv+" B") : (p.wv+(F.unit?(" \\u00b7 "+F.unit):""))) ) : (F.unit||F.label||""));',
      'hover-figure')

open(OUT,"w",encoding="utf-8").write(text)
print("OK: perf (no per-move queryRenderedFeatures); path arcs dampened K=0.35; hover figures")
