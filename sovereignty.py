import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding='utf-8').read()
lines=text.split('\n')
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
def bb(poly):
    xs=[];ys=[]
    def w(o):
        if isinstance(o[0],(int,float)): xs.append(o[0]);ys.append(o[1])
        else:
            for x in o: w(x)
    w(poly); return min(xs),min(ys),max(xs),max(ys)
tw=next(f for f in MAP['features'] if f['properties'].get('iso3')=='TWN')['properties']
tw.update({'name':'Taiwan','population':23400000,'popDensity':650,'gdppc':33000,'lifeExp':80.9,'internet':92,
  'govtype':'Semi-presidential republic','regime':'Full democracy','langFamily':'Sino-Tibetan',
  'language':'Mandarin Chinese','languages':'Mandarin Chinese','langCount':1,'lgbtStatus':'Marriage equality',
  'climateLabel':'Temperate','relMajority':'Folk','relMajorityLabel':'Folk / Traditional',
  'relBreakdown':'{"Folk":44,"Buddhism":21,"Unaffiliated":19,"Christianity":5,"Other":11}',
  'co2pc':11,'debtGdp':28,'under5mort':4,'matmort':10,'physicians':3.0,'healthspend':6.6,'hiv':0.1})
TW_NUM={'popdensity':650,'gdppc':33000,'lifeexp':80.9,'internet':92,'govdebt':28,'co2pc':11,
        'under5mort':4,'matmort':10,'physicians':3.0,'healthspend':6.6,'hiv':0.1}
for L in META['layers']:
    k=L['key'];t=L.get('type');cp='color_'+k
    if t=='numeric' and k in TW_NUM: tw[cp]=ramp(float(TW_NUM[k]),L['stops'])
    elif t=='categorical':
        leg={d['label']:d['color'] for d in (L.get('legend') or [])}
        if tw.get(L['prop']) in leg: tw[cp]=leg[tw[L['prop']]]
sd=META.setdefault('subnatData',{}).setdefault('USA',{})
sd['Alaska']={"Christianity":62,"Unaffiliated":31,"Other":7}
sd['Hawaii']={"Christianity":63,"Unaffiliated":26,"Buddhism":6,"Other":5}
sd['Puerto Rico']={"Christianity":85,"Unaffiliated":11,"Other":4}
pd=META.setdefault('partyData',{}).setdefault('USA',{})
pd['Alaska']=13.1; pd['Hawaii']=-23.5
usa_sps=next(f for f in MAP['features'] if f['properties'].get('iso3')=='USA')['geometry']['coordinates']
ak=[];hi=[]
for sp in usa_sps:
    x0,y0,x1,y1=bb(sp);cx,cy=(x0+x1)/2,(y0+y1)/2
    if (-161<cx<-154) and (18<cy<23): hi.append(sp)
    elif (-180<cx<-130) and cy>50: ak.append(sp)
pr_geom=next(f for f in MAP['features'] if f['properties'].get('iso3')=='PRI')['geometry']
META['subnat']['USA']['extra']=[
  {"type":"Feature","properties":{"name":"Alaska"},"geometry":{"type":"MultiPolygon","coordinates":ak}},
  {"type":"Feature","properties":{"name":"Hawaii"},"geometry":{"type":"MultiPolygon","coordinates":hi}},
  {"type":"Feature","properties":{"name":"Puerto Rico"},"geometry":pr_geom}]
pr=next(f for f in MAP['features'] if f['properties'].get('iso3')=='PRI')['properties']
pr['govtype']='Unincorporated US territory'; pr['color_govtype']='#8a93a3'
pr['statusNote']=("Unincorporated U.S. territory. Residents are U.S. citizens but cannot vote for "
  "President and have no voting member of Congress. Its political future \u2014 remaining a territory, "
  "U.S. statehood, or independence \u2014 is unresolved and actively debated.")
RD={"Full democracy":"Free elections, broad civil liberties, independent courts and press.",
 "Flawed democracy":"Free elections, but weak participation, media or governance flaws.",
 "Hybrid regime":"Irregular elections; opposition and press pressured; weak rule of law.",
 "Authoritarian":"Little pluralism; power concentrated; dissent suppressed."}
for it in next(L for L in META['layers'] if L['key']=='regime')['legend']:
    if it['label'] in RD: it['desc']=RD[it['label']]
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: {n}x"; return t.replace(a,b)
if 'if(cfg.extra)' not in text:
    text=patch(text,'  src.then(gj=>{\n    const regions=META.subnatData[iso3]||{};',
      '  src.then(gj=>{\n    if(cfg.extra){ const _have=new Set(gj.features.map(f=>f.properties[cfg.nameProp])); cfg.extra.forEach(ef=>{ if(!_have.has(ef.properties[cfg.nameProp])) gj.features.push(ef); }); }\n    const regions=META.subnatData[iso3]||{};','loader')
if 'const REGIME_DESC=' not in text:
    text=patch(text,'function openCountry(p){',
      'const REGIME_DESC={"Full democracy":"Free elections, broad civil liberties, independent courts and press.","Flawed democracy":"Free elections, but weak participation, media or governance flaws.","Hybrid regime":"Irregular elections; opposition and press pressured; weak rule of law.","Authoritarian":"Little pluralism; power concentrated; dissent suppressed."};\nfunction openCountry(p){','rconst')
if 'p.statusNote' not in text:
    text=patch(text,'  let h="";\n\n  // Religion breakdown',
      '  let h="";\n  if(p.statusNote) h+=`<div class="sec"><h4>Political status</h4><div class="note">${p.statusNote}</div></div>`;\n\n  // Religion breakdown','status')
if 'REGIME_DESC[p.regime]' not in text:
    text=patch(text,'    if(p.regime) h+=`<div class="stat"><span class="k">Regime type</span><span class="v">${p.regime}</span></div>`;',
      '    if(p.regime) h+=`<div class="stat"><span class="k">Regime type</span><span class="v">${p.regime}</span></div>`;\n    if(p.regime&&REGIME_DESC[p.regime]) h+=`<div class="note" style="margin:3px 0 0">${REGIME_DESC[p.regime]}</div>`;','rnote')
if 'it.desc?' not in text:
    text=patch(text,'    c.legend.forEach(it=>{ b+=`<div class="lg-row"><span class="sw" style="background:${it.color}"></span>${it.label}</div>`; });',
      '    c.legend.forEach(it=>{ b+=`<div class="lg-row"><span class="sw" style="background:${it.color}"></span>${it.label}</div>`+(it.desc?`<div style="font-size:11px;color:#8a97a8;margin:-1px 0 6px 22px;line-height:1.3">${it.desc}</div>`:""); });','ldesc')
open(OUT,'w',encoding='utf-8').write(text)
print("OK")
