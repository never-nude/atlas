import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'const wlo=m?' not in text:
    OLD=('  const m=isMobileV();\n'
     '  const opI=["interpolate",["linear"],["get","w"], 0, m?0.34:0.14, 1, m?0.80:0.42];\n'
     '  const wI =["interpolate",["linear"],["get","w"], 0, m?1.1:0.5, 1, m?3.6:2.4];\n'
     '  const rI =["interpolate",["linear"],["get","w"], 0, m?1.7:1.1, 1, m?3.6:2.6];\n'
     '  map.setPaintProperty("flow-lines","line-opacity", flowIso?["case",["==",["get","c"],flowIso], opI, 0.05]:opI);\n'
     '  map.setPaintProperty("flow-lines","line-width", wI);\n'
     '  map.setPaintProperty("flow-dots","circle-opacity", flowIso?["case",["==",["get","c"],flowIso], 0.9, 0.04]:0.9);\n'
     '  map.setPaintProperty("flow-dots","circle-radius", rI);')
    NEW=('  const m=isMobileV();\n'
     '  const wlo=m?1.1:0.7, whi=m?3.6:2.6, rlo=m?1.7:1.3, rhi=m?3.6:2.8;\n'
     '  const opI=["interpolate",["linear"],["get","w"], 0, m?0.40:0.24, 1, m?0.85:0.52];\n'
     '  const wI=["interpolate",["linear"],["zoom"], 1.5,["interpolate",["linear"],["get","w"],0,wlo,1,whi], 9,["interpolate",["linear"],["get","w"],0,wlo*3,1,whi*3]];\n'
     '  const rI=["interpolate",["linear"],["zoom"], 1.5,["interpolate",["linear"],["get","w"],0,rlo,1,rhi], 9,["interpolate",["linear"],["get","w"],0,rlo*2.4,1,rhi*2.4]];\n'
     '  map.setPaintProperty("flow-lines","line-opacity", flowIso?["case",["==",["get","c"],flowIso], opI, 0.05]:opI);\n'
     '  map.setPaintProperty("flow-lines","line-width", wI);\n'
     '  map.setPaintProperty("flow-dots","circle-opacity", flowIso?["case",["==",["get","c"],flowIso], 0.95, 0.04]:0.95);\n'
     '  map.setPaintProperty("flow-dots","circle-radius", rI);')
    text=patch(text,OLD,NEW,'applyFlowStyle')
if 'Math.max(5,Math.round(pts.length/6)' not in text:
    text=patch(text,'nDots:1+Math.round((e.w/wmax)*2)','nDots:Math.max(5,Math.round(pts.length/6)+Math.round((e.w/wmax)*3))','nDots')
open(OUT,"w",encoding="utf-8").write(text)
print("OK")
