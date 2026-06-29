import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
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
sd.setdefault('Alaska',{"Christianity":62,"Unaffiliated":31,"Other":7})
sd.setdefault('Hawaii',{"Christianity":63,"Unaffiliated":26,"Buddhism":6,"Other":5})
pd=META.setdefault('partyData',{}).setdefault('USA',{})
pd.setdefault('Alaska',13.1); pd.setdefault('Hawaii',-23.5)
pr=next(f for f in MAP['features'] if f['properties'].get('iso3')=='PRI')['properties']
pr['govtype']='US territory (Commonwealth)'; pr['color_govtype']='#8a93a3'
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print("OK")
