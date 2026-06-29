import json, re, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'flow_currents' not in text, 'paths layers already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
'''    if(flowFocusIso && e.from!==flowFocusIso && e.to!==flowFocusIso) return;
    const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to]; if(!a||!b) return;
    const pts=gcPoints(a,b,48);''',
'''    if(flowFocusIso && e.from && e.to && e.from!==flowFocusIso && e.to!==flowFocusIso) return;
    let pts;
    if(e.path){ pts=[]; for(let k=0;k<e.path.length-1;k++){ const sg=gcPoints(e.path[k],e.path[k+1],14); pts=pts.concat(k?sg.slice(1):sg); } }
    else { const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to]; if(!a||!b) return; pts=gcPoints(a,b,48); }''',
'engine-waypoints')
text=patch(text,
'''function setFlowBase(key){
  if(subOn) return;
  const role=rolesFor(key, flowIso), pairs=[];''',
'''function setFlowBase(key){
  if(subOn) return;
  if(FLOWS[key]&&FLOWS[key].geo){ map.setPaintProperty("fills","fill-color","#162130"); map.setPaintProperty("fills","fill-opacity",0.72); return; }
  const role=rolesFor(key, flowIso), pairs=[];''',
'engine-geobase')
text=patch(text,'  { const RL=roleLabels(key);','  if(!F.geo){ const RL=roleLabels(key);','engine-geolegend')
text=patch(text,
  'counterfeit:{source:"Producer",transit:"Transit hub",consumer:"Market"}};',
  'counterfeit:{source:"Producer",transit:"Transit hub",consumer:"Market"},\n'
  '    flights:{source:"Hub",transit:"Hub",consumer:"Hub"},\n'
  '    refugees:{source:"Origin",transit:"Transit",consumer:"Host"},\n'
  '    students:{source:"Origin",transit:"Both",consumer:"Destination"}};',
  'role-labels')
FLOWS_JS = r'''  currents: {
    label: "Ocean currents", group: "Natural systems", geo: true,
    unit: "major surface currents (warm / cold)",
    desc: "The great ocean surface currents that move heat around the planet — warm currents (red) carry tropical heat poleward; cold currents (blue) return.",
    color: "#e0683f", dotColor:"#ffd9c4",
    legend: "Flowing lines trace major ocean currents. Red = warm current, blue = cold. Dots show the direction of flow.",
    note: "Schematic paths of the major surface currents (Gulf Stream, Kuroshio, Antarctic Circumpolar, Humboldt, Agulhas, etc.). Illustrative, not exact streamlines.",
    sources: [{label:"NOAA — Ocean currents", url:"https://oceanservice.noaa.gov/education/tutorial_currents/"}],
    edges: [
      {c:"#e0683f",w:3,path:[[-80,25],[-75,32],[-68,39],[-58,43],[-40,48],[-22,53],[-8,57],[2,60]]},
      {c:"#e0683f",w:2.5,path:[[122,20],[128,27],[138,34],[150,39],[162,41],[175,40]]},
      {c:"#e0683f",w:2,path:[[-38,-10],[-44,-20],[-50,-30],[-56,-38],[-58,-44]]},
      {c:"#e0683f",w:2,path:[[35,-24],[30,-32],[24,-36],[18,-37],[12,-36]]},
      {c:"#4f93d6",w:2,path:[[-125,46],[-123,39],[-119,31],[-113,23],[-108,18]]},
      {c:"#4f93d6",w:2.5,path:[[-73,-44],[-72,-33],[-75,-22],[-80,-10],[-82,-2],[-83,4]]},
      {c:"#4f93d6",w:2,path:[[-14,32],[-18,24],[-21,16],[-22,10],[-21,4]]},
      {c:"#4f93d6",w:1.6,path:[[-52,48],[-50,44],[-66,41],[-72,40]]},
      {c:"#7fb0d6",w:3.5,path:[[-60,-57],[-20,-55],[20,-56],[70,-58],[120,-60],[170,-62],[-150,-61],[-100,-59],[-65,-58]]}
    ]
  },
  flyways: {
    label: "Bird migration flyways", group: "Natural systems", geo: true,
    unit: "major global flyways",
    desc: "The great aerial highways billions of migratory birds follow between northern breeding grounds and southern wintering grounds each year.",
    color: "#74c98a", dotColor:"#dff7e4",
    legend: "Each ribbon is a major flyway; dots show the southbound direction of autumn migration.",
    note: "The world's principal flyways (East Atlantic, Mediterranean/Black Sea, East Asian-Australasian, the two American flyways, Central Asian). Schematic.",
    sources: [{label:"Convention on Migratory Species — Flyways", url:"https://www.cms.int/en/page/flyways"}],
    edges: [
      {w:2,path:[[18,74],[10,64],[2,52],[-4,41],[-11,29],[-16,16],[-15,6]]},
      {w:2,path:[[55,70],[40,58],[30,46],[26,34],[29,21],[31,9]]},
      {w:2.5,path:[[150,72],[142,55],[126,38],[114,22],[120,4],[132,-12],[146,-32]]},
      {w:2,path:[[-95,72],[-86,55],[-80,38],[-78,22],[-70,7],[-60,-12],[-58,-32]]},
      {w:2,path:[[-150,68],[-132,54],[-122,40],[-110,22],[-90,4],[-76,-16],[-72,-38]]},
      {w:1.6,path:[[78,70],[74,55],[72,38],[76,22],[80,10]]}
    ]
  },
  dust: {
    label: "Saharan dust", group: "Natural systems", geo: true,
    unit: "trans-Atlantic dust transport",
    desc: "Each year the wind lifts hundreds of millions of tonnes of Saharan dust across the Atlantic — fertilising the Amazon and feeding Caribbean skies.",
    color: "#d4a857", dotColor:"#f6e6b8",
    legend: "Dust plumes carried west on the trade winds from the Sahara toward the Amazon and Caribbean.",
    note: "Schematic of the trans-Atlantic Saharan Air Layer transport (strongest in northern summer).",
    sources: [{label:"NASA Earth Observatory — Saharan dust", url:"https://earthobservatory.nasa.gov/images/event/86353/saharan-dust"}],
    edges: [
      {w:2.5,path:[[2,18],[-18,16],[-38,13],[-55,9],[-64,4],[-62,-3]]},
      {w:2,path:[[-8,23],[-32,21],[-56,18],[-72,16],[-80,17]]}
    ]
  },
  silkroad: {
    label: "Silk Road", group: "Historic routes", geo: true,
    unit: "overland + maritime trade routes (c. 130 BCE - 1450 CE)",
    desc: "The network of routes that carried silk, spices, ideas, religions and plagues between China, Central Asia, Persia, the Arab world and Europe.",
    color: "#d9a441", dotColor:"#f4e2b0",
    legend: "Gold = the overland caravan routes; amber = the maritime spice route. Dots run west, as the silk did.",
    note: "Composite of the principal overland and maritime Silk Road corridors. Routes shifted over centuries; this is illustrative.",
    sources: [{label:"UNESCO — Silk Roads Programme", url:"https://en.unesco.org/silkroad/"}],
    edges: [
      {c:"#d9a441",w:2.5,path:[[109,34],[100,38],[88,43],[75,40],[64,39],[52,35],[44,33],[36,34],[29,41]]},
      {c:"#c9893a",w:2,path:[[113,23],[108,9],[98,6],[80,7],[72,18],[58,23],[50,15],[43,13],[35,22]]}
    ]
  },
  voyages: {
    label: "Age of Exploration", group: "Historic routes", geo: true,
    unit: "landmark voyages, 1405-1522",
    desc: "Four voyages that stitched the world together: Zheng He's treasure fleets, da Gama to India, Columbus to the Americas, and Magellan's circumnavigation.",
    color: "#6ec6b0", dotColor:"#e6fff7",
    legend: "Each colored track is one expedition; dots follow the direction of the outward voyage.",
    note: "Approximate tracks of Zheng He (1405-33), da Gama (1497-99), Columbus (1492), and the Magellan-Elcano circumnavigation (1519-22).",
    sources: [{label:"Britannica — Age of Discovery", url:"https://www.britannica.com/topic/European-exploration"}],
    edges: [
      {c:"#6ec6b0",w:2,path:[[120,32],[110,15],[100,6],[80,8],[60,18],[45,12],[40,-4]]},
      {c:"#5fae5f",w:2,path:[[-9,38],[-17,15],[-10,-15],[18,-35],[35,-25],[45,-5],[73,15]]},
      {c:"#e0a93a",w:2,path:[[-6,37],[-18,28],[-40,21],[-60,18],[-74,20]]},
      {c:"#c45fae",w:2,path:[[-6,37],[-25,5],[-48,-25],[-68,-53],[-100,-33],[-150,-8],[123,11]]}
    ]
  },
  flights: {
    label: "Flight corridors", group: "Infrastructure & travel",
    unit: "busiest international air corridors",
    desc: "Some of the world's busiest international passenger air corridors — the great-circle paths jets actually fly.",
    color: "#6ed0e0", dotColor:"#e3fbff",
    legend: "Each arc is a heavily-trafficked international flight corridor.",
    note: "A selection of high-traffic international corridors (great-circle paths between hub countries). Illustrative, not a full network.",
    sources: [{label:"OAG / IATA — air traffic statistics", url:"https://www.iata.org/en/publications/economics/"}],
    edges: [
      {from:"HKG",to:"TWN",w:3},{from:"KOR",to:"JPN",w:3},{from:"ARE",to:"IND",w:3},
      {from:"GBR",to:"USA",w:3},{from:"USA",to:"MEX",w:2.5},{from:"GBR",to:"ESP",w:2.5},
      {from:"ARE",to:"GBR",w:2.5},{from:"USA",to:"CAN",w:2.5},{from:"JPN",to:"CHN",w:2.5},
      {from:"KOR",to:"CHN",w:2},{from:"THA",to:"CHN",w:2},{from:"USA",to:"JPN",w:2.5},
      {from:"AUS",to:"NZL",w:2},{from:"QAT",to:"IND",w:2},{from:"SAU",to:"EGY",w:2},
      {from:"FRA",to:"USA",w:2},{from:"DEU",to:"USA",w:2},{from:"BRA",to:"USA",w:2},
      {from:"SGP",to:"AUS",w:2},{from:"IND",to:"GBR",w:2}
    ]
  },
  shipping: {
    label: "Shipping lanes", group: "Infrastructure & travel", geo: true,
    unit: "major maritime trade lanes & chokepoints",
    desc: "The arteries of seaborne trade — and the chokepoints they squeeze through: Malacca, Suez, Panama, Hormuz, Gibraltar, the Cape.",
    color: "#3fb6a8", dotColor:"#d6fff8",
    legend: "Each lane is a primary container-shipping route; the tight bends are the world's strategic chokepoints.",
    note: "Schematic of the main East-West shipping lanes through Malacca, Suez, the Cape, and Panama. Illustrative.",
    sources: [{label:"UNCTAD — Review of Maritime Transport", url:"https://unctad.org/rmt"}],
    edges: [
      {w:3,path:[[122,31],[114,5],[101,3],[80,6],[57,12],[44,13],[33,28],[32,31],[18,34],[6,37],[-5,36],[-2,44],[4,52]]},
      {w:2.5,path:[[122,31],[140,34],[165,40],[-170,42],[-140,40],[-122,35],[-118,34]]},
      {w:2,path:[[121,31],[155,18],[-175,8],[-120,7],[-90,8],[-80,9],[-79,9.2],[-75,15],[-74,20]]},
      {w:2,path:[[72,18],[63,22],[57,25],[56,26.5],[57,25.5],[60,22],[68,15],[78,8]]}
    ]
  },
  refugees: {
    label: "Refugee flows", group: "Human movement",
    unit: "major forced-displacement corridors",
    desc: "Where the world's refugees have fled — forced displacement from conflict and crisis to neighbouring host countries.",
    color: "#e0792f", dotColor:"#ffd9b8",
    legend: "Each arc is a major refugee corridor; dots flow from origin toward the host country.",
    note: "Major corridors from UNHCR Global Trends. Most refugees are hosted in neighbouring countries; figures are relative.",
    sources: [{label:"UNHCR — Global Trends / Refugee Data", url:"https://www.unhcr.org/refugee-statistics/"}],
    edges: [
      {from:"SYR",to:"TUR",w:3.5},{from:"SYR",to:"LBN",w:2},{from:"SYR",to:"JOR",w:2},
      {from:"AFG",to:"IRN",w:3},{from:"AFG",to:"PAK",w:3},{from:"UKR",to:"POL",w:3},
      {from:"UKR",to:"DEU",w:2.5},{from:"VEN",to:"COL",w:3},{from:"VEN",to:"PER",w:2},
      {from:"SSD",to:"UGA",w:2.5},{from:"SSD",to:"SDN",w:2},{from:"MMR",to:"BGD",w:2.5},
      {from:"SOM",to:"KEN",w:2},{from:"SOM",to:"ETH",w:2},{from:"COD",to:"UGA",w:2},
      {from:"SDN",to:"TCD",w:2},{from:"SDN",to:"EGY",w:2},{from:"BDI",to:"TZA",w:1.5},
      {from:"CAF",to:"CMR",w:1.5},{from:"ERI",to:"ETH",w:1.5}
    ]
  },
  students: {
    label: "International students", group: "Human movement",
    unit: "major international student corridors",
    desc: "Where students cross borders to study — the flows of tertiary students from home countries to the big education destinations.",
    color: "#6ea8fe", dotColor:"#dcebff",
    legend: "Each arc is a major international-student corridor; dots flow from origin toward the host country.",
    note: "Top corridors from UNESCO UIS / OECD inbound-mobility data. Figures are relative.",
    sources: [{label:"UNESCO Institute for Statistics — Global Flow of Tertiary Students", url:"https://uis.unesco.org/en/uis-student-flow"}],
    edges: [
      {from:"CHN",to:"USA",w:3.5},{from:"IND",to:"USA",w:3},{from:"CHN",to:"GBR",w:2.5},
      {from:"IND",to:"GBR",w:2},{from:"CHN",to:"AUS",w:2.5},{from:"IND",to:"AUS",w:2.5},
      {from:"CHN",to:"CAN",w:2},{from:"IND",to:"CAN",w:2.5},{from:"VNM",to:"USA",w:1.5},
      {from:"KOR",to:"USA",w:1.5},{from:"CHN",to:"JPN",w:1.5},{from:"NGA",to:"GBR",w:1.5},
      {from:"NGA",to:"USA",w:1.5},{from:"SAU",to:"USA",w:1.5},{from:"FRA",to:"CAN",w:1.5},
      {from:"NPL",to:"AUS",w:1.5},{from:"MAR",to:"FRA",w:1.5},{from:"DEU",to:"GBR",w:1.2},
      {from:"PAK",to:"GBR",w:1.5},{from:"BRA",to:"USA",w:1.2}
    ]
  },
'''
text=patch(text,'const FLOWS = {','const FLOWS = {\n'+FLOWS_JS,'flows-insert')
lines=text.split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
new=[]
for grp,items in [
  ("Natural systems",[("currents","Ocean currents"),("flyways","Bird migration flyways"),("dust","Saharan dust")]),
  ("Historic routes",[("silkroad","Silk Road"),("voyages","Age of Exploration")]),
  ("Infrastructure & travel",[("flights","Flight corridors"),("shipping","Shipping lanes")]),
  ("Human movement",[("refugees","Refugee flows"),("students","International students")]),
]:
  for k,lbl in items:
    new.append({"group":grp,"key":"flow_"+k,"label":lbl,"type":"flow","flowKey":k})
ci=next(i for i,l in enumerate(L) if l.get('key')=='flow_counterfeit')
L[ci+1:ci+1]=new
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
open(OUT,'w',encoding='utf-8').write(text)
print("OK: 9 path layers across 4 groups + waypoint engine extension")
