import json, sys, os
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
IND=[('SH.DYN.MORT','under5mort',1),('SH.STA.MMRT','matmort',0),('SH.MED.PHYS.ZS','physicians',2),
     ('SH.XPD.CHEX.GD.ZS','healthspend',1),('SH.DYN.AIDS.ZS','hiv',1),('SH.H2O.SMDW.ZS','water',1),
     ('SH.STA.SMSS.ZS','sanitation',1)]
WB={}
for code,prop,dec in IND:
    fn=f"wb_{code}.json"
    if not os.path.exists(fn): sys.exit(f"MISSING {fn} — run the curl download into this folder first.")
    d=json.load(open(fn)); latest={}
    for r in d[1]:
        iso=r.get('countryiso3code'); v=r.get('value'); yr=r.get('date')
        if not iso or v is None or len(iso)!=3: continue
        if iso not in latest or yr>latest[iso][0]: latest[iso]=(yr,v)
    for iso,(yr,v) in latest.items():
        WB.setdefault(iso,{})[prop]=(int(round(v)) if dec==0 else round(v,dec))
lines=open(INP,encoding='utf-8').read().split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
def _hx(c):c=c.lstrip('#');return(int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t):return'#%02x%02x%02x'%t
def ramp(v,stops):
    st=[(s['v'],s['color']) for s in stops]
    if v<=st[0][0]:return st[0][1]
    if v>=st[-1][0]:return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i];v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0;a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]
stops={L['key']:L['stops'] for L in META['layers'] if L.get('type')=='numeric'}
n={}
for f in MAP['features']:
    p=f['properties']; rec=WB.get(p.get('iso3'))
    if not rec: continue
    for k,v in rec.items():
        p[k]=v; p['color_'+k]=ramp(float(v),stops[k]); n[k]=n.get(k,0)+1
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print("OK filled:",n)
