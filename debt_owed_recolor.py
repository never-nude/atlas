import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding='utf-8').read()
lines=text.split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
OWED=[(1,"#ffe3b3"),(8,"#ffb066"),(20,"#f47b3c"),(35,"#d83f24"),(60,"#a01414")]
def _hx(c):c=c.lstrip('#');return(int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t):return'#%02x%02x%02x'%t
def ramp(v,st):
    if v<=st[0][0]:return st[0][1]
    if v>=st[-1][0]:return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i];v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0;a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]
n=0
for f in MAP['features']:
    p=f['properties']
    if p.get('debtorDebt') is not None: p['color_debtorDebt']=ramp(float(p['debtorDebt']),OWED); n+=1
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
text='\n'.join(lines)
def patch(t,a,b,label):
    c=t.count(a); assert c==1, f"{label}: {c}x"; return t.replace(a,b)
OLDG='<div class="lg-grad" style="background:linear-gradient(90deg,#1a2433,${F.color})"></div>'
NEWG='<div class="lg-grad" style="background:linear-gradient(90deg,${F.dir===\"in\"?\"#ffe3b3\":\"#1a2433\"},${F.dir===\"in\"?\"#a01414\":F.color})"></div>'
if '?\"#ffe3b3\"' not in text: text=patch(text,OLDG,NEWG,'legend-gradient')
if 'pale = little owed' not in text:
    text=patch(text,'total owed (brighter = deeper in debt)','total owed (pale = little owed, deep red = heavily indebted; grey = no data)','wording')
open(OUT,'w',encoding='utf-8').write(text)
print(f"OK: re-baked {n}; legend + wording fixed")
