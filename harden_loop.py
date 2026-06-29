import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'try{\n    if(!last)last=t;' not in text:
    text=patch(text,
      'function frame(t){\n    if(!last)last=t; const dt=Math.min((t-last)/1000,0.1); last=t;',
      'function frame(t){\n    try{\n    if(!last)last=t; const dt=Math.min((t-last)/1000,0.1); last=t;',
      'frame-try-open')
    text=patch(text,
      '    }\n    requestAnimationFrame(frame);\n  }\n  requestAnimationFrame(frame);',
      '    }\n    }catch(_e){ try{console.warn("atlas frame skipped:",_e&&_e.message);}catch(_){} }\n    requestAnimationFrame(frame);\n  }\n  requestAnimationFrame(frame);',
      'frame-try-close')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: master loop crash-proofed")
