#!/usr/bin/env python3
"""Make the 3D moving nodes prominent on Codex's lifted-arc renderer.
The dots render but are tiny (2-4px) and same hue as the thick ribbons, so they don't read as
moving nodes. Enlarge them and give each a glowing white core so they clearly travel the arcs.
python3 dots_pop.py index.html index.html   (idempotent)"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()

# 1) bigger point size
OLD_SZ='gl_PointSize=mix(mix(2.0,4.2,a_w),mix(5.0,10.0,a_w),zt);'
NEW_SZ='gl_PointSize=mix(mix(4.6,7.6,a_w),mix(9.0,17.0,a_w),zt);'
if OLD_SZ in text: text=text.replace(OLD_SZ,NEW_SZ)

# 2) glowing white core in the dot fragment shader
OLD_FR='float a=smoothstep(1.0,0.15,d)*v_color.a*mix(0.82,1.0,v_w); fragColor=vec4(v_color.rgb,a); }'
NEW_FR='float a=smoothstep(1.0,0.15,d)*v_color.a*mix(0.82,1.0,v_w); vec3 col=mix(v_color.rgb,vec3(1.0),smoothstep(0.55,0.0,d)*0.7); fragColor=vec4(col,a); }'
if OLD_FR in text: text=text.replace(OLD_FR,NEW_FR)

open(OUT,"w",encoding="utf-8").write(text)
ok = (NEW_SZ in text) and (NEW_FR in text)
print("OK: dots enlarged + white core" if ok else "WARN: one or both anchors not found")
