#!/usr/bin/env python3
"""Add 3 illicit-trade flow layers to Atlas (Illicit flows group):
   human trafficking, wildlife trafficking, counterfeit goods.
Each reuses the source/transit/destination country shading. Idempotent.
   python3 illicit_flows.py index.html index.html"""
import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"

# origin -> destination edges (w = relative prominence; transit countries appear as both from & to)
TRAFFICKING=[ # UNODC Global Report on Trafficking in Persons
 ('MEX','USA',3),('GTM','USA',1.5),('HND','USA',1.5),('SLV','USA',1),('VEN','COL',1.5),
 ('MMR','THA',2.5),('KHM','THA',1.5),('LAO','THA',1),('MMR','CHN',2),('PRK','CHN',1.5),
 ('NPL','IND',2),('BGD','IND',2),('BGD','SAU',1.5),('NPL','QAT',1),('IDN','MYS',2),('PHL','MYS',1),
 ('PHL','ARE',1.5),('IND','ARE',1.5),('ETH','SAU',2),('KEN','SAU',1),('UGA','ARE',1),
 ('NGA','LBY',2),('LBY','ITA',2),('MAR','ESP',1),('UKR','POL',1.5),('MDA','ROU',1),('ROU','ITA',1),
 ('UZB','RUS',1.5),('TJK','RUS',1),('KGZ','RUS',1),
]
WILDLIFE=[ # UNODC World Wildlife Crime Report / CITES — Africa & SE Asia -> China/Vietnam
 ('KEN','CHN',2),('TZA','CHN',2),('ZAF','VNM',2.5),('MOZ','VNM',1.5),('COD','CHN',1.5),
 ('CMR','VNM',1.5),('AGO','VNM',1.5),('NGA','CHN',2),('NGA','VNM',2),('UGA','CHN',1),('TGO','CHN',1),
 ('MMR','CHN',2),('LAO','CHN',1.5),('IDN','CHN',1.5),('MYS','CHN',1.5),('THA','CHN',1),('VNM','CHN',2.5),
 ('ARE','CHN',1),('SGP','CHN',1),('IND','CHN',1.5),('NPL','CHN',1),('BRA','CHN',1),('MDG','CHN',1),
]
COUNTERFEIT=[ # OECD/EUIPO Trade in Counterfeit & Pirated Goods — China/HK dominant producers
 ('CHN','USA',4),('CHN','DEU',2),('CHN','FRA',2),('CHN','GBR',2),('CHN','ITA',1.5),('CHN','JPN',1.5),
 ('CHN','KOR',1),('CHN','AUS',1),('CHN','BRA',1.5),('CHN','MEX',1.5),('CHN','RUS',1.5),
 ('HKG','USA',2),('HKG','DEU',1.5),('TUR','DEU',1.5),('TUR','GBR',1),('IND','USA',1.5),('IND','GBR',1),
 ('THA','USA',1),('VNM','USA',1),('CHN','ARE',1.5),('ARE','SAU',1),('CHN','SGP',1),('SGP','AUS',1),
]

def edges_js(edges):
    return ',\n'.join('      '+','.join(f'{{from:"{a}",to:"{b}",w:{w}}}' for a,b,w in edges[k:k+3])
                      for k in range(0,len(edges),3))

FLOWS_JS = '''  trafficking: {
    label: "Human trafficking",
    group: "Illicit flows",
    unit: "relative corridor prominence (detected victims)",
    desc: "Cross-border human-trafficking corridors — people moved from origin countries to destinations for forced labour or sexual exploitation. Most trafficking is in fact within borders; only transregional corridors are drawn.",
    color: "#c45fae", dotColor:"#f0c4e6",
    legend: "Each arc is a documented transregional trafficking corridor; dots flow from origin toward destination.",
    note: "Illustrative corridors from the UNODC Global Report on Trafficking in Persons (2024). Magnitudes are relative, not victim counts; many domestic and smaller flows are omitted. A sensitive topic shown for awareness, not precision.",
    sources: [
      {label:"UNODC — Global Report on Trafficking in Persons 2024", url:"https://www.unodc.org/unodc/en/human-trafficking/global-report-on-trafficking-in-persons.html"}
    ],
    edges: [
''' + edges_js(TRAFFICKING) + '''
    ]
  },
  wildlife: {
    label: "Wildlife trafficking",
    group: "Illicit flows",
    unit: "relative corridor prominence (seizures)",
    desc: "Illegal wildlife trade — ivory, rhino horn, pangolin scales and more, moved from source (poaching) countries through transit hubs to demand markets, overwhelmingly China and Vietnam.",
    color: "#5fae5f", dotColor:"#d6f0c4",
    legend: "Each arc is a major wildlife-trafficking route; dots flow from source toward the demand market.",
    note: "Illustrative routes from the UNODC World Wildlife Crime Report and CITES seizure data. Vietnam, Malaysia, UAE and Singapore act as transit hubs. Magnitudes are relative.",
    sources: [
      {label:"UNODC — World Wildlife Crime Report", url:"https://www.unodc.org/unodc/en/data-and-analysis/wildlife.html"},
      {label:"CITES — trade & seizure data", url:"https://cites.org/"}
    ],
    edges: [
''' + edges_js(WILDLIFE) + '''
    ]
  },
  counterfeit: {
    label: "Counterfeit goods",
    group: "Illicit flows",
    unit: "relative trade value (seizures)",
    desc: "Trade in counterfeit and pirated goods — from producer economies (China and Hong Kong dominate) through transit hubs to consumer markets in the US and Europe.",
    color: "#d9a441", dotColor:"#f5e6b0",
    legend: "Each arc is a major counterfeit-goods trade route; dots flow from producer toward market.",
    note: "Illustrative routes from the OECD/EUIPO 'Trade in Counterfeit and Pirated Goods' studies. China + Hong Kong account for the large majority of seizures; UAE, Singapore and Turkey are transit points. Magnitudes are relative.",
    sources: [
      {label:"OECD/EUIPO — Trade in Counterfeit and Pirated Goods", url:"https://www.oecd.org/gov/risk/trade-in-counterfeit-and-pirated-goods-g2g9f533-en.htm"}
    ],
    edges: [
''' + edges_js(COUNTERFEIT) + '''
    ]
  },
'''

text=open(INP,encoding='utf-8').read()
assert 'trafficking: {' not in text, 'Illicit flows already applied - aborting.'

def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)

# 1) insert the three FLOWS datasets
text=patch(text,'const FLOWS = {','const FLOWS = {\n'+FLOWS_JS,'flows-insert')
# 2) role labels for the three new flows
text=patch(text,
  'cables:{source:"Cable landing",transit:"Cable hub",consumer:"Cable landing"}};',
  'cables:{source:"Cable landing",transit:"Cable hub",consumer:"Cable landing"},\n'
  '    trafficking:{source:"Origin",transit:"Transit",consumer:"Destination"},\n'
  '    wildlife:{source:"Source (poaching)",transit:"Transit hub",consumer:"Demand market"},\n'
  '    counterfeit:{source:"Producer",transit:"Transit hub",consumer:"Market"}};',
  'role-labels')
# 3) META layers (after flow_arms, in 'Illicit flows' group)
lines=text.split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
new=[{'group':'Illicit flows','key':'flow_'+k,'label':lbl,'type':'flow','flowKey':k}
     for k,lbl in [('trafficking','Human trafficking'),('wildlife','Wildlife trafficking'),('counterfeit','Counterfeit goods')]]
ia=next(i for i,l in enumerate(L) if l.get('key')=='flow_arms')
L[ia+1:ia+1]=new
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)

open(OUT,'w',encoding='utf-8').write(text)
print(f"OK: added trafficking({len(TRAFFICKING)}), wildlife({len(WILDLIFE)}), counterfeit({len(COUNTERFEIT)}) edges.")
print("illicit layers now:", [l.get('key') for l in META['layers'] if l.get('group')=='Illicit flows'])
