import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'function unwrapLng(' not in text:
    helpers=('function unwrapLng(pts){ for(let i=1;i<pts.length;i++){ let d=pts[i][0]-pts[i-1][0];'
      ' while(d>180){pts[i][0]-=360;d-=360;} while(d<-180){pts[i][0]+=360;d+=360;} } return pts; }\n'
      'function _lighten(hex,t){ if(!hex||hex[0]!=="#"||hex.length<7) return hex||"#cfe2ff";'
      ' const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);'
      ' const m=v=>Math.round(v+(255-v)*t); return "#"+[m(r),m(g),m(b)].map(v=>v.toString(16).padStart(2,"0")).join(""); }\n'
      'function buildFlowGeo(key){')
    text=patch(text,'function buildFlowGeo(key){',helpers,'helpers')
if 'pts=unwrapLng(pts);' not in text:
    text=patch(text,
      'else { const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to]; if(!a||!b) return; pts=gcPoints(a,b,48); }',
      'else { const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to]; if(!a||!b) return; pts=gcPoints(a,b,48); }\n    pts=unwrapLng(pts);',
      'unwrap')
if '_lighten(e.c||F.color' not in text:
    text=patch(text,'const col=e.c||F.color, dotCol=e.dc||e.c||F.dotColor||"#cfe2ff";',
      'const col=e.c||F.color, dotCol=e.dc||_lighten(e.c||F.color,0.5);','dot-colour')
if 'it.two ? _lighten(' not in text:
    text=patch(text,'const dc = it.two ? (i0<it.pts.length/2?F.fromColor:F.toColor) : it.dotCol;',
      'const dc = it.two ? _lighten(i0<it.pts.length/2?F.fromColor:F.toColor,0.5) : it.dotCol;','two-tone-dots')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: arctic loop unwrap + brighter nodes")
