import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
CATS=('\n    cats: [\n      {label:"Labour / family migration", color:"#6ea8fe"},\n'
      '      {label:"Mainly displacement (refugees)", color:"#d4793a"}\n    ],')
if CATS in text: text=text.replace(CATS,'')
for e in ['{from:"MMR",to:"THA",w:1.9,c:"#d4793a"}','{from:"AFG",to:"PAK",w:1.6,c:"#d4793a"}']:
    if e in text: text=text.replace(e, e.replace(',c:"#d4793a"',''))
OLDLEG=' Orange corridors are mainly displacement (refugees / forced).'
if OLDLEG in text: text=text.replace(OLDLEG,' Thickness scales with zoom for readability.')
if 'wlo=m?1.1:0.7' in text:
    text=patch(text,'  const wlo=m?1.1:0.7, whi=m?3.6:2.6, rlo=m?1.7:1.3, rhi=m?3.6:2.8;',
      '  const wlo=m?1.7:1.2, whi=m?4.4:3.2, rlo=m?1.9:1.5, rhi=m?4.0:3.0;','line-base')
    text=patch(text,'  const opI=["interpolate",["linear"],["get","w"], 0, m?0.40:0.24, 1, m?0.85:0.52];',
      '  const opI=["interpolate",["linear"],["get","w"], 0, m?0.66:0.58, 1, m?0.95:0.90];','line-opacity')
if 'dotCol=e.dc||e.c||' not in text:
    text=patch(text,'const col=e.c||F.color, dotCol=e.dc||F.dotColor||"#cfe2ff";',
      'const col=e.c||F.color, dotCol=e.dc||e.c||F.dotColor||"#cfe2ff";','dot-colour')
open(OUT,"w",encoding="utf-8").write(text)
print("OK")
