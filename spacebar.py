import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if '/*spacebar*/' not in text:
    anchor='  if(pb) pb.onclick=()=>{ paused=!paused; pb.textContent=paused?"▶":"⏸"; };'
    listener=anchor+'''
  /*spacebar*/ document.addEventListener("keydown",e=>{
    if(e.code!=="Space" && e.key!==" ") return;
    const el=e.target; if(el && (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)||el.isContentEditable)) return;
    e.preventDefault();
    paused=!paused; if(!paused) simLast=0;
    const tb=document.getElementById("tbPlay"); if(tb) tb.textContent=paused?"▶":"⏸";
    const pbn=document.getElementById("playBtn"); if(pbn) pbn.textContent=paused?"▶ Resume":"⏸ Pause";
  });'''
    text=patch(text,anchor,listener,'spacebar-listener')
oldhint='<div id="hint">Drag to spin · scroll to zoom · click a country to drill in</div>'
newhint='<div id="hint">Drag to spin · scroll to zoom · space to pause · click a country to drill in</div>'
if oldhint in text: text=text.replace(oldhint,newhint)
open(OUT,"w",encoding="utf-8").write(text)
print("OK")
