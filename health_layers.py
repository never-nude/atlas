#!/usr/bin/env python3
"""Add a 'Health' group to Atlas: 7 choropleths + a brain-drain flow + a Health
panel section. Also idempotently folds in the debt color-prop fix
(color_debtgdp -> color_govdebt). Run: python3 health_layers.py index.html index.html"""
import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"

# ---- per-country data (ISO3). Approx, research-grade: WHO GHO, World Bank,
#      UN IGME (child mort), UN MMEIG (maternal), UNAIDS (HIV), WHO/UNICEF JMP (water/san).
U5M={'NER':115,'NGA':110,'SOM':108,'SLE':105,'CAF':100,'TCD':99,'SSD':98,'GIN':95,'MLI':90,
'BEN':84,'BFA':82,'COD':79,'GNB':73,'LSO':73,'CIV':72,'CMR':70,'MOZ':70,'LBR':70,'MDG':66,
'AGO':68,'TGO':63,'PAK':63,'HTI':60,'YEM':58,'ZMB':58,'AFG':55,'SDN':55,'SWZ':50,'ZWE':50,
'COM':50,'TZA':49,'GMB':48,'ETH':47,'GHA':44,'COG':44,'GAB':42,'UGA':42,'PNG':42,'LAO':42,
'MMR':42,'TKM':41,'KEN':41,'NAM':39,'RWA':39,'SEN':38,'MWI':38,'ZAF':33,'BWA':32,'TJK':32,
'IND':31,'BGD':29,'NPL':27,'BTN':27,'KHM':26,'PHL':26,'IRQ':24,'VEN':24,'GTM':24,'BOL':24,
'DZA':22,'IDN':22,'SYR':21,'EGY':19,'VNM':19,'SLB':19,'AZE':19,'MAR':18,'PRY':18,'KGZ':17,
'HND':16,'TUN':16,'NIC':14,'JOR':14,'MNG':14,'UZB':14,'BRA':14,'IRN':13,'MEX':13,'COL':13,
'ECU':13,'PER':12,'OMN':11,'ARM':11,'KAZ':10,'TUR':9,'ARG':9,'KWT':9,'GEO':9,'UKR':8,'THA':8,
'MYS':8,'CHN':7,'LKA':7,'LBN':7,'CHL':7,'URY':7,'SAU':7,'ARE':7,'QAT':6,'USA':6,'CAN':5,
'RUS':5,'NZL':5,'GBR':4,'FRA':4,'DEU':4,'POL':4,'DNK':4,'NLD':4,'CHE':4,'AUS':4,'GRC':4,
'ISR':4,'ITA':3,'ESP':3,'KOR':3,'IRL':3,'PRT':3,'BLR':3,'JPN':2,'SWE':2,'NOR':2,'FIN':2,'SGP':2}
MMR={'SSD':1150,'TCD':1060,'NGA':1050,'CAF':830,'AFG':620,'SOM':620,'LBR':650,'GIN':550,
'COD':550,'BEN':520,'KEN':530,'LSO':560,'SLE':440,'MLI':440,'NER':440,'GNB':460,'MRT':460,
'GMB':460,'CIV':480,'CMR':440,'MOZ':430,'ETH':400,'TGO':400,'MDG':390,'MWI':380,'ZWE':360,
'HTI':350,'SDN':270,'BFA':260,'SEN':260,'VEN':260,'RWA':250,'TZA':240,'SWZ':240,'GHA':310,
'ZMB':220,'AGO':220,'TLS':200,'NAM':200,'PNG':190,'BWA':180,'YEM':180,'MMR':180,'NPL':170,
'IDN':170,'KHM':160,'PAK':150,'BOL':130,'LAO':130,'ZAF':130,'BGD':120,'PHL':120,'IND':100,
'GTM':90,'DZA':80,'HND':70,'PER':70,'BRA':70,'COL':70,'MAR':70,'MEX':60,'IRQ':50,'VNM':46,
'MNG':40,'EGY':30,'SYR':30,'THA':30,'LKA':30,'CHN':23,'IRN':22,'USA':21,'TUR':17,'TJK':17,
'UKR':17,'SAU':16,'KAZ':13,'RUS':14,'CAN':11,'GBR':10,'ARE':9,'KOR':8,'FIN':8,'QAT':8,
'FRA':8,'DEU':7,'CHE':7,'SGP':7,'ITA':5,'SWE':5,'ESP':4,'JPN':4,'NLD':4,'AUS':3,'ISR':3,'NOR':2}
PHYS={'CUB':8.4,'MCO':7.5,'GRC':6.3,'PRT':5.5,'AUT':5.4,'GEO':5.1,'URY':5.1,'NOR':5.0,'ESP':4.6,
'FIN':4.6,'BLR':4.5,'DEU':4.4,'CHE':4.4,'SWE':4.3,'DNK':4.2,'BGR':4.2,'ITA':4.1,'CZE':4.1,
'KAZ':4.0,'ARG':4.0,'AUS':3.8,'RUS':3.8,'NLD':3.7,'NZL':3.6,'ISR':3.6,'IRL':3.5,'HUN':3.5,
'HRV':3.5,'POL':3.4,'FRA':3.3,'CRI':3.3,'BEL':3.1,'SAU':3.1,'SRB':3.1,'GBR':3.0,'UKR':3.0,
'ROU':3.0,'ARE':2.9,'CHL':2.8,'CAN':2.7,'USA':2.6,'JPN':2.5,'KOR':2.5,'QAT':2.5,'CHN':2.4,
'MEX':2.4,'UZB':2.4,'BRA':2.3,'COL':2.3,'JOR':2.3,'LBN':2.1,'TUR':2.0,'VEN':1.7,'DZA':1.7,
'IRN':1.6,'BOL':1.6,'PER':1.4,'TUN':1.3,'LKA':1.0,'PAK':1.0,'NPL':0.8,'PHL':0.8,'VNM':0.8,
'ZAF':0.8,'THA':0.9,'EGY':0.7,'MAR':0.7,'IND':0.7,'BGD':0.7,'IDN':0.6,'NAM':0.6,'YEM':0.5,
'LAO':0.4,'NGA':0.4,'BWA':0.4,'AFG':0.3,'SDN':0.3,'KHM':0.2,'KEN':0.2,'MDG':0.2,'ZWE':0.21,
'GHA':0.18,'UGA':0.17,'ZMB':0.13,'MLI':0.13,'CMR':0.13,'RWA':0.13,'COD':0.07,'SLE':0.07,
'TCD':0.06,'TZA':0.06,'MWI':0.05,'LBR':0.05,'NER':0.04,'SOM':0.02,'SEN':0.09,'MOZ':0.09,'ETH':0.1}
HSP={'USA':17,'CUB':12,'DEU':12.8,'CAN':12.9,'ARM':12,'LSO':12,'FRA':12.2,'GBR':12,'AUT':11.5,
'SWE':11.4,'NOR':11.4,'CHE':11.3,'JPN':11,'NLD':11,'BEL':11,'DNK':10.8,'PRT':10.6,'AUS':10.6,
'ESP':10.5,'NZL':10,'FIN':10,'ARG':10,'BRA':9.6,'ITA':9.6,'URY':9.5,'SVN':9.5,'GRC':9,'CHL':9,
'CZE':9,'ZAF':8.5,'NAM':8.5,'COL':8,'LBN':8,'MOZ':8,'KOR':8.4,'GEO':7.6,'UKR':7.7,'JOR':7.5,
'ISR':7.5,'CRI':7.5,'KHM':7,'HUN':7,'BOL':7,'TUN':7,'RWA':7,'MWI':7,'SWZ':7,'IRL':7,'RUS':7.5,
'IRN':6.7,'DZA':6,'PER':6,'MEX':6,'NER':6,'UZB':6,'BWA':6,'SGP':6,'POL':6.5,'MAR':5.3,'NPL':5,
'PHL':5.5,'SAU':5.5,'THA':5,'KWT':5,'SOM':5,'VEN':5,'TCD':5,'ARE':5,'VNM':4.3,'KEN':4.3,
'IRQ':4,'NGA':4,'ETH':3.5,'TZA':4,'UGA':4,'GHA':4,'EGY':4.5,'SDN':4.5,'YEM':4,'MLI':4,
'SEN':4,'CMR':4,'COD':4,'MDG':4,'MYS':4,'QAT':4,'TUR':4.6,'AZE':4,'IND':3,'IDN':3.4,'PAK':3,
'LAO':3,'ZWE':3,'KAZ':3.8,'BGD':2.5,'AFG':14}
HIV={'SWZ':27.9,'LSO':21,'BWA':18.6,'ZAF':18.3,'NAM':11.8,'MOZ':11.5,'ZWE':11,'ZMB':11,
'GNQ':7,'MWI':7.1,'UGA':5.2,'TZA':4.3,'KEN':4.0,'CAF':3.6,'COG':3.4,'GAB':3,'CMR':2.9,
'BHS':2.5,'RWA':2.5,'SSD':2.1,'CIV':2,'AGO':1.9,'HTI':1.8,'GIN':1.4,'NGA':1.3,'GHA':1.7,
'JAM':1.5,'GUY':1.5,'SLE':1.5,'BDI':1,'TCD':1,'THA':1.0,'RUS':1.0,'EST':1.0,'UKR':0.9,
'ETH':0.9,'MLI':0.8,'COD':0.7,'MMR':0.6,'MDA':0.6,'BRA':0.5,'GEO':0.5,'COL':0.5,'USA':0.4,
'IDN':0.4,'MEX':0.4,'PER':0.4,'ARG':0.4,'KAZ':0.3,'VNM':0.3,'IND':0.2,'UZB':0.2,'PAK':0.2,
'CHN':0.1,'NPL':0.2,'KHM':0.5,'PHL':0.3,'MAR':0.1,'EGY':0.1,'TUR':0.1,'IRN':0.2,'PNG':0.9}
WAT={'TCD':46,'CAF':46,'COD':47,'ETH':50,'MDG':53,'PNG':45,'SSD':41,'NER':56,'SOM':56,'UGA':56,
'AGO':57,'TZA':61,'KEN':62,'MOZ':63,'YEM':64,'GIN':64,'SLE':64,'ZMB':65,'BEN':66,'GNB':67,
'HTI':67,'TGO':69,'MWI':70,'LBR':75,'AFG':75,'BFA':76,'ZWE':77,'NGA':78,'KHM':78,'CMR':78,
'MLI':83,'SEN':85,'LAO':85,'GHA':88,'MAR':88,'IND':93,'IDN':93,'CHN':94,'PHL':95,'VNM':97,
'BGD':98,'BRA':98,'NPL':90,'PAK':90,'MEX':99,'EGY':99,'PER':92,'BOL':93,'COL':97,'ZAF':94,
'GTM':90,'HND':95,'NIC':84,'IRQ':97,'SYR':95,'IRN':96,'JOR':99}
SAN={'ETH':9,'TCD':12,'MDG':12,'SSD':16,'SLE':17,'NER':18,'TGO':19,'UGA':20,'COD':22,'BEN':23,
'GHA':25,'BFA':25,'LBR':28,'TZA':32,'ZMB':33,'KEN':35,'CIV':36,'ZWE':36,'MOZ':38,'HTI':38,
'SOM':39,'GIN':39,'CMR':41,'NGA':44,'MWI':47,'AGO':52,'SEN':56,'BGD':58,'PAK':68,'NPL':78,
'IND':81,'PHL':79,'KHM':80,'LAO':80,'MMR':80,'IDN':87,'BRA':90,'CHN':92,'MEX':92,'MAR':92,
'VNM':95,'EGY':97,'PER':80,'BOL':68,'COL':93,'ZAF':79,'GTM':72,'IRQ':95,'IRN':90}

# (value, hex) ramps.  'bad' = high is worse (red high). 'good' = high is better (green high). 'neutral' diverging.
RAMP={
'under5mort':[(2,"#0d3b2a"),(5,"#1d6b46"),(15,"#c9c24a"),(40,"#e08a3a"),(80,"#c0443a"),(115,"#7a1f2b")],
'matmort':[(3,"#0d3b2a"),(15,"#1d6b46"),(70,"#c9c24a"),(250,"#e08a3a"),(550,"#c0443a"),(1100,"#7a1f2b")],
'physicians':[(0.05,"#7a1f2b"),(0.3,"#c0443a"),(0.8,"#e08a3a"),(1.8,"#c9c24a"),(3.5,"#5aa75a"),(6,"#2a9d6f")],
'healthspend':[(2,"#241433"),(4,"#3b2f6b"),(6,"#3f6fb0"),(9,"#36a87f"),(13,"#9bd070"),(18,"#f2e85c")],
'hiv':[(0.1,"#0d3b2a"),(0.5,"#1d6b46"),(2,"#c9c24a"),(6,"#e08a3a"),(15,"#c0443a"),(28,"#7a1f2b")],
'water':[(40,"#7a1f2b"),(60,"#c0443a"),(78,"#e08a3a"),(90,"#c9c24a"),(97,"#5aa75a"),(100,"#2a9d6f")],
'sanitation':[(20,"#7a1f2b"),(45,"#c0443a"),(65,"#e08a3a"),(82,"#c9c24a"),(95,"#5aa75a"),(100,"#2a9d6f")],
}
NODATA="#262f3d"
# layer config: key -> (prop, data, label, short, fmtType, unit)
LAYERS=[
 ('under5mort',U5M,'Under-5 mortality','U5 mortality','dec1','deaths per 1,000 live births'),
 ('matmort',MMR,'Maternal mortality','Maternal mortality','int','deaths per 100,000 live births'),
 ('physicians',PHYS,'Physicians / 1,000','Physicians','dec1','physicians per 1,000 people'),
 ('healthspend',HSP,'Health spending (% GDP)','Health spend','dec1','% of GDP'),
 ('hiv',HIV,'HIV prevalence','HIV prevalence','dec1','% of adults 15-49'),
 ('water',WAT,'Safe drinking water','Safe water','int','% of population'),
 ('sanitation',SAN,'Sanitation access','Sanitation','int','% of population'),
]

def _hx(c): c=c.lstrip('#'); return (int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t): return '#%02x%02x%02x'%t
def ramp(v,st):
    if v is None: return NODATA
    if v<=st[0][0]: return st[0][1]
    if v>=st[-1][0]: return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i]; v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0; a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)

# ---- load + idempotent debt fix ----
text=open(INP,encoding='utf-8').read()
assert 'color_under5mort' not in text[:200000], 'Health already applied - aborting.'
text=text.replace('color_debtgdp','color_govdebt')   # fold in debt fix (no-op if done)
lines=text.split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))

# bake choropleths
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
counts={}
for f in MAP['features']:
    p=f['properties']; iso=p.get('iso3')
    if not iso: continue
    for key,data,_,_,_,_ in LAYERS:
        if iso in data:
            p[key]=data[iso]; p['color_'+key]=ramp(data[iso],RAMP[key]); counts[key]=counts.get(key,0)+1
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'

# META: add 7 choropleths + brain-drain flow, in a new 'Health' group, after 'lgbt'
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
newcfgs=[]
for key,data,label,short,fmt,unit in LAYERS:
    newcfgs.append({'group':'Health','key':key,'label':label,'type':'numeric','prop':key,
        'short':short,'fmtType':fmt,'unit':unit,'stops':[{'v':v,'color':c} for v,c in RAMP[key]]})
newcfgs.append({'group':'Health','key':'flow_braindrain','label':'Medical brain drain','type':'flow','flowKey':'braindrain'})
li=next(i for i,l in enumerate(L) if l.get('key')=='lgbt')
L[li+1:li+1]=newcfgs
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)

# FLOWS.braindrain (origin -> destination; dots show direction of the outflow)
BD=[('PHL','USA',6),('IND','USA',5),('IND','GBR',4),('EGY','SAU',4),('PHL','SAU',3),('IND','ARE',3),
('NGA','GBR',3),('NGA','USA',2),('PHL','GBR',2),('PAK','GBR',2),('ZWE','GBR',2),('ZAF','GBR',2),
('SDN','SAU',2),('MEX','USA',2),('DZA','FRA',2),('MAR','FRA',2),('ROU','DEU',2),('IND','AUS',2),
('PHL','CAN',2),('GHA','GBR',1),('KEN','GBR',1),('LKA','GBR',1),('ZMB','GBR',1),('MWI','GBR',1),
('CUB','BRA',1),('POL','GBR',1),('GHA','USA',1),('IRN','USA',1)]
flow_js='''  braindrain: {
    label: "Medical brain drain",
    group: "Health",
    unit: "relative scale (foreign-trained doctors & nurses)",
    desc: "Emigration of doctors and nurses from their training country to wealthier destinations — a major strain on health systems in origin countries.",
    color: "#5fd0c0", dotColor:"#d6fff5",
    legend: "Each arc is a major health-worker migration corridor; dots flow from the origin (training) country toward the destination.",
    note: "Illustrative corridors based on OECD and WHO health-workforce migration data; magnitudes are relative, not absolute counts. (Health-flow layer — more, e.g. vaccine/aid flows, can be added the same way.)",
    sources: [
      {label:"WHO — Global strategy on human resources for health", url:"https://www.who.int/publications/i/item/9789241511131"},
      {label:"OECD — International Migration of Health Workers", url:"https://www.oecd.org/en/topics/health-workforce.html"}
    ],
    edges: [
'''+',\n'.join('      '+','.join(f'{{from:"{a}",to:"{b}",w:{w}}}' for a,b,w in BD[k:k+3]) for k in range(0,len(BD),3))+'''
    ]
  },
'''
text=patch(text,'const FLOWS = {','const FLOWS = {\n'+flow_js,'flows-braindrain')

# Health panel section, inserted after the Debt section
debt_tail='''    else if(dp.domestic) h+=`<div class="note" style="margin-top:6px">Predominantly domestic / market-held debt — not bilateral.</div>`;
    h+=`</div>`;
  }'''
health_sec=debt_tail+'''
  if(p.under5mort!=null||p.matmort!=null||p.physicians!=null||p.healthspend!=null||p.hiv!=null||p.water!=null||p.sanitation!=null){
    h+=`<div class="sec"><h4>Health</h4>`;
    if(p.under5mort!=null) h+=`<div class="stat"><span class="k">Under-5 mortality</span><span class="v">${p.under5mort} / 1,000</span></div>`;
    if(p.matmort!=null) h+=`<div class="stat"><span class="k">Maternal mortality</span><span class="v">${p.matmort} / 100k</span></div>`;
    if(p.physicians!=null) h+=`<div class="stat"><span class="k">Physicians</span><span class="v">${p.physicians} / 1,000</span></div>`;
    if(p.healthspend!=null) h+=`<div class="stat"><span class="k">Health spending</span><span class="v">${p.healthspend}% of GDP</span></div>`;
    if(p.hiv!=null) h+=`<div class="stat"><span class="k">HIV prevalence</span><span class="v">${p.hiv}% (15-49)</span></div>`;
    if(p.water!=null) h+=`<div class="stat"><span class="k">Safe water</span><span class="v">${p.water}%</span></div>`;
    if(p.sanitation!=null) h+=`<div class="stat"><span class="k">Sanitation</span><span class="v">${p.sanitation}%</span></div>`;
    h+=`</div>`;
  }'''
text=patch(text,debt_tail,health_sec,'inject-health-panel')

# ---- flow polish: role-based country shading for EVERY flow + stronger US->UKR debt ----
OLD_BASE='''function setFlowBase(key){
  if(subOn) return;
  if(isIllicit(key)){
    const role=rolesFor(key, flowIso), pairs=[];
    Object.entries(role).forEach(([iso,r])=>{ pairs.push(iso, ROLE_COL[r]); });
    map.setPaintProperty("fills","fill-color", pairs.length?["match",["get","iso3"], ...pairs, ROLE_COL.none]:ROLE_COL.none);
    map.setPaintProperty("fills","fill-opacity",0.8);
  } else {
    map.setPaintProperty("fills","fill-color",colorExpr("popdensity"));
    map.setPaintProperty("fills","fill-opacity",0.45);
  }
}'''
NEW_BASE='''function roleLabels(key){
  const M={migration:{source:"Origin",transit:"Both ways",consumer:"Destination"},
    remittances:{source:"Sender",transit:"Both",consumer:"Receiver"},
    trade:{source:"Net exporter",transit:"Both",consumer:"Net importer"},
    debt:{source:"Creditor",transit:"Both",consumer:"Debtor"},
    braindrain:{source:"Origin (trains them)",transit:"Both",consumer:"Destination"},
    cables:{source:"Cable landing",transit:"Cable hub",consumer:"Cable landing"}};
  return M[key]||{source:"Source",transit:"Transit",consumer:"Consumer"};
}
function setFlowBase(key){
  if(subOn) return;
  const role=rolesFor(key, flowIso), pairs=[];
  Object.entries(role).forEach(([iso,r])=>{ pairs.push(iso, ROLE_COL[r]); });
  map.setPaintProperty("fills","fill-color", pairs.length?["match",["get","iso3"], ...pairs, ROLE_COL.none]:ROLE_COL.none);
  map.setPaintProperty("fills","fill-opacity",0.82);
}'''
text=patch(text,OLD_BASE,NEW_BASE,'flow-base-roles')
OLD_LEG='''  if(isIllicit(key)){
    b+=`<div class="lg-row" style="margin-top:9px;color:var(--muted);font-size:10.5px">Country shading — role in ${flowIso?"this substance's":"these"} routes:</div>`;
    [["Source",ROLE_COL.source],["Transit",ROLE_COL.transit],["Consumer",ROLE_COL.consumer],["Not in routes",ROLE_COL.none]].forEach(([lab,col])=>{
      b+=`<div class="lg-row"><span class="sw" style="background:${col}"></span>${lab}</div>`;
    });
  }'''
NEW_LEG='''  { const RL=roleLabels(key);
    b+=`<div class="lg-row" style="margin-top:9px;color:var(--muted);font-size:10.5px">Country shading — role in ${flowIso?"this category's":"these"} flows:</div>`;
    [[RL.source,ROLE_COL.source],[RL.transit,ROLE_COL.transit],[RL.consumer,ROLE_COL.consumer],["Not involved",ROLE_COL.none]].forEach(([lab,col])=>{
      b+=`<div class="lg-row"><span class="sw" style="background:${col}"></span>${lab}</div>`;
    });
  }'''
text=patch(text,OLD_LEG,NEW_LEG,'flow-legend-roles')
text=patch(text,'{from:"USA",to:"UKR",w:8}','{from:"USA",to:"UKR",w:20}','us-ukr-debt')

open(OUT,'w',encoding='utf-8').write(text)
print("OK: health baked:", counts)
print("layers:", [l.get('key') for l in META['layers']])
