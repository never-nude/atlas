#!/usr/bin/env python3
"""Add two debt choropleths derived from the FLOWS.debt arcs:
   - 'Bilateral debt owed'   (sum of incoming edge weights, US$bn)
   - 'Bilateral credit extended' (sum of outgoing edge weights, US$bn)
Consolidates all debt layers under a 'Debt' group. Run AFTER health_layers.py.
   python3 debt_split.py index.html index.html"""
import json, re, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"

text=open(INP,encoding='utf-8').read()
assert 'color_debtorDebt' not in text[:200000], 'debt_split already applied - aborting.'

# ---- extract the bilateral-debt edges (the block flagged twoTone) ----
i=text.index('twoTone: true')          # unique to the debt flow
e0=text.index('edges: [', i); e1=text.index(']', e0)
edges=re.findall(r'\{from:"(\w+)",to:"(\w+)",w:([\d.]+)\}', text[e0:e1])
owed={}; lent={}
for a,b,w in edges:
    w=float(w); lent[a]=lent.get(a,0)+w; owed[b]=owed.get(b,0)+w
rnd=lambda x: int(round(x)) if x>=1 else round(x,1)
owed={k:rnd(v) for k,v in owed.items()}; lent={k:rnd(v) for k,v in lent.items()}

CRED_STOPS=[(0.5,"#10302c"),(5,"#176b5e"),(20,"#23a08c"),(50,"#46c9b2"),(120,"#7fe6d2"),(220,"#c9fff5")]
DEBT_STOPS=[(1,"#241208"),(8,"#6e2f12"),(20,"#b0481f"),(35,"#e0603a"),(60,"#f4a07a")]
NODATA="#262f3d"
def _hx(c):c=c.lstrip('#');return(int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t):return'#%02x%02x%02x'%t
def ramp(v,st):
    if v is None:return NODATA
    if v<=st[0][0]:return st[0][1]
    if v>=st[-1][0]:return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i];v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0;a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]

lines=text.split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
for f in MAP['features']:
    p=f['properties']; iso=p.get('iso3')
    if not iso: continue
    if iso in owed: p['debtorDebt']=owed[iso]; p['color_debtorDebt']=ramp(owed[iso],DEBT_STOPS)
    if iso in lent: p['creditorDebt']=lent[iso]; p['color_creditorDebt']=ramp(lent[iso],CRED_STOPS)
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'

META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
owed_cfg={'group':'Debt','key':'debtorDebt','label':'Bilateral debt owed','type':'numeric','prop':'debtorDebt',
  'short':'Owed (bilateral)','fmtType':'money','unit':'US$ billions owed to foreign governments',
  'stops':[{'v':v,'color':c} for v,c in DEBT_STOPS]}
lent_cfg={'group':'Debt','key':'creditorDebt','label':'Bilateral credit extended','type':'numeric','prop':'creditorDebt',
  'short':'Lent (bilateral)','fmtType':'money','unit':'US$ billions lent to other governments',
  'stops':[{'v':v,'color':c} for v,c in CRED_STOPS]}
# consolidate all debt layers under one 'Debt' group
for l in L:
    if l.get('key') in ('govdebt','flow_debt'): l['group']='Debt'
gi=next(i for i,l in enumerate(L) if l.get('key')=='govdebt')
L[gi+1:gi+1]=[owed_cfg,lent_cfg]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)

# panel: add owes/lends rows right after the Govt-debt stat line
anchor='''    if(g!=null) h+=`<div class="stat"><span class="k">Govt debt</span><span class="v">≈ ${g}% of GDP</span></div>`;'''
add=anchor+'''
    if(p.creditorDebt) h+=`<div class="stat"><span class="k">Lends bilaterally</span><span class="v">≈ $${p.creditorDebt}B</span></div>`;
    if(p.debtorDebt) h+=`<div class="stat"><span class="k">Owes bilaterally</span><span class="v">≈ $${p.debtorDebt}B</span></div>`;'''
assert text.count(anchor)==1
text=text.replace(anchor,add)

# ---- antimeridian-safe day/night + ocean grids (kills the wedge/gap at 180deg on the globe) ----
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"grid anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
'''function sunGrid(){
  const feats=[], STEP=4;
  for(let la=-90; la<90; la+=STEP){ for(let lo=-180; lo<180; lo+=STEP){
    feats.push({type:"Feature",properties:{cx:lo+STEP/2,cy:la+STEP/2,op:0},
      geometry:{type:"Polygon",coordinates:[[[lo,la],[lo+STEP,la],[lo+STEP,la+STEP],[lo,la+STEP],[lo,la]]]}});
  }}
  SUNFC={type:"FeatureCollection",features:feats}; shadeGrid(); return SUNFC;
}''',
'''function sunGrid(){
  const feats=[], STEP=4, EW=180-1e-4;   // stop a hair short of ±180 so no cell edge sits on the antimeridian (avoids globe-projection wedge)
  for(let la=-90; la<90; la+=STEP){ for(let lo=-EW; lo<EW; lo+=STEP){ const lo2=Math.min(lo+STEP,EW);
    feats.push({type:"Feature",properties:{cx:(lo+lo2)/2,cy:la+STEP/2,op:0},
      geometry:{type:"Polygon",coordinates:[[[lo,la],[lo2,la],[lo2,la+STEP],[lo,la+STEP],[lo,la]]]}});
  }}
  SUNFC={type:"FeatureCollection",features:feats}; shadeGrid(); return SUNFC;
}''','sungrid')
text=patch(text,
'''function oceanGrid(){ const feats=[],S=4;
  for(let la=-90; la<90; la+=S) for(let lo=-180; lo<180; lo+=S)
    feats.push({type:"Feature",properties:{},geometry:{type:"Polygon",coordinates:[[[lo,la],[lo+S,la],[lo+S,la+S],[lo,la+S],[lo,la]]]}});
  return {type:"FeatureCollection",features:feats}; }''',
'''function oceanGrid(){ const feats=[],S=4,EW=180-1e-4;   // antimeridian-safe (no vertex exactly on ±180)
  for(let la=-90; la<90; la+=S) for(let lo=-EW; lo<EW; lo+=S){ const lo2=Math.min(lo+S,EW);
    feats.push({type:"Feature",properties:{},geometry:{type:"Polygon",coordinates:[[[lo,la],[lo2,la],[lo2,la+S],[lo,la+S],[lo,la]]]}}); }
  return {type:"FeatureCollection",features:feats}; }''','oceangrid')

open(OUT,'w',encoding='utf-8').write(text)
print(f"OK: debt owed for {len(owed)} countries, credit for {len(lent)}.")
print("top creditors:", sorted(lent.items(),key=lambda x:-x[1])[:5])
print("top debtors:", sorted(owed.items(),key=lambda x:-x[1])[:5])
