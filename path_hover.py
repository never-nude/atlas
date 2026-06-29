import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'function isoName(' not in text:
    text=patch(text,'function unwrapLng(pts){',
      'let _ISO_NAME=null;\n'
      'function isoName(c){ if(!_ISO_NAME){ _ISO_NAME={}; try{ MAPDATA.features.forEach(f=>{ _ISO_NAME[f.properties.iso3]=f.properties.name; }); }catch(_){} } return _ISO_NAME[c]||c; }\n'
      'function unwrapLng(pts){','isoName')
for a in ['from:e.from,to:e.to,c:col}','from:e.from,to:e.to,c:F.fromColor}','from:e.from,to:e.to,c:F.toColor}']:
    if a.replace('}','')+',nm:e.nm' not in text:
        text=text.replace(a, a[:-1]+',nm:e.nm||null,amt:e.amt||null}')
anchor='  map.on("mouseleave","fills",()=>{ if(subOn)return; map.getCanvas().style.cursor=""; map.setFilter("hover",["==","iso3",""]); pop.remove(); });'
if 'mousemove","flow-lines"' not in text:
    handler=anchor+'\n'+(
      '  map.on("mousemove","flow-lines",e=>{ if(subOn||!flowActive()) return;\n'
      '    map.getCanvas().style.cursor="pointer"; const p=e.features[0].properties, F=FLOWS[flowKey]||{};\n'
      '    const title=p.nm || ((p.from&&p.to)?(isoName(p.from)+" \\u2192 "+isoName(p.to)):(F.label||"Route"));\n'
      '    const sub=p.amt || F.unit || F.label || "";\n'
      '    map.setFilter("hover",["==","iso3",""]);\n'
      '    pop.setLngLat(e.lngLat).setHTML(\'<div class="pop-name">\'+title+\'</div>\'+(sub?\'<div class="pop-sub">\'+sub+\'</div>\':\'\')).addTo(map);\n'
      '  });\n'
      '  map.on("mouseleave","flow-lines",()=>{ if(!subOn) map.getCanvas().style.cursor=""; });')
    text=patch(text,anchor,handler,'line-hover')
fills_anchor='  map.on("mousemove","fills",e=>{\n    if(subOn) return;'
if 'queryRenderedFeatures(e.point,{layers:["flow-lines"]}).length) return;' not in text:
    text=patch(text,fills_anchor,
      fills_anchor+'\n    if(flowActive() && map.queryRenderedFeatures(e.point,{layers:["flow-lines"]}).length) return;',
      'fills-defer')
OLD_CUR='''[
      {c:"#e0683f",w:3,path:[[-80,25],[-75,32],[-68,39],[-58,43],[-40,48],[-22,53],[-8,57],[2,60]]},
      {c:"#e0683f",w:2.5,path:[[122,20],[128,27],[138,34],[150,39],[162,41],[175,40]]},
      {c:"#e0683f",w:2,path:[[-38,-10],[-44,-20],[-50,-30],[-56,-38],[-58,-44]]},
      {c:"#e0683f",w:2,path:[[35,-24],[30,-32],[24,-36],[18,-37],[12,-36]]},
      {c:"#4f93d6",w:2,path:[[-125,46],[-123,39],[-119,31],[-113,23],[-108,18]]},
      {c:"#4f93d6",w:2.5,path:[[-73,-44],[-72,-33],[-75,-22],[-80,-10],[-82,-2],[-83,4]]},
      {c:"#4f93d6",w:2,path:[[-14,32],[-18,24],[-21,16],[-22,10],[-21,4]]},
      {c:"#4f93d6",w:1.6,path:[[-52,48],[-50,44],[-66,41],[-72,40]]},
      {c:"#7fb0d6",w:3.5,path:[[-60,-57],[-20,-55],[20,-56],[70,-58],[120,-60],[170,-62],[-150,-61],[-100,-59],[-65,-58]]}
    ]'''
NEW_CUR='''[
      {nm:"Gulf Stream",amt:"warm \\u00b7 ~30 Sv",c:"#e0683f",w:2.4,path:[[-80,25],[-75,32],[-68,39],[-58,43],[-40,48],[-22,53],[-8,57],[2,60]]},
      {nm:"Kuroshio Current",amt:"warm \\u00b7 ~25 Sv",c:"#e0683f",w:2.2,path:[[122,20],[128,27],[138,34],[150,39],[162,41],[175,40]]},
      {nm:"Brazil Current",amt:"warm \\u00b7 ~15 Sv",c:"#e0683f",w:1.7,path:[[-38,-10],[-44,-20],[-50,-30],[-56,-38],[-58,-44]]},
      {nm:"Agulhas Current",amt:"warm \\u00b7 ~70 Sv",c:"#e0683f",w:3.0,path:[[35,-24],[30,-32],[24,-36],[18,-37],[12,-36]]},
      {nm:"California Current",amt:"cold \\u00b7 ~10 Sv",c:"#4f93d6",w:1.4,path:[[-125,46],[-123,39],[-119,31],[-113,23],[-108,18]]},
      {nm:"Humboldt Current",amt:"cold \\u00b7 ~18 Sv",c:"#4f93d6",w:1.9,path:[[-73,-44],[-72,-33],[-75,-22],[-80,-10],[-82,-2],[-83,4]]},
      {nm:"Canary Current",amt:"cold \\u00b7 ~10 Sv",c:"#4f93d6",w:1.4,path:[[-14,32],[-18,24],[-21,16],[-22,10],[-21,4]]},
      {nm:"Labrador Current",amt:"cold \\u00b7 ~5 Sv",c:"#4f93d6",w:1.0,path:[[-52,48],[-50,44],[-66,41],[-72,40]]},
      {nm:"Antarctic Circumpolar Current",amt:"~150 Sv \\u2014 largest on Earth",c:"#7fb0d6",w:4.0,path:[[-60,-57],[-20,-55],[20,-56],[70,-58],[120,-60],[170,-62],[-150,-61],[-100,-59],[-65,-58]]}
    ]'''
if 'Antarctic Circumpolar Current' not in text:
    text=patch(text,OLD_CUR,NEW_CUR,'currents-enrich')
open(OUT,"w",encoding="utf-8").write(text)
print("OK")
