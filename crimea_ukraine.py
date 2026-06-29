import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
lines=open(INP,encoding='utf-8').read().split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
def bbox(poly):
    xs=[];ys=[]
    def walk(o):
        if isinstance(o[0],(int,float)): xs.append(o[0]);ys.append(o[1])
        else:
            for x in o: walk(x)
    walk(poly); return min(xs),min(ys),max(xs),max(ys)
def is_crimea(poly):
    x0,y0,x1,y1=bbox(poly); cx,cy=(x0+x1)/2,(y0+y1)/2
    return 32<cx<37 and 44<cy<46.6 and (x1-x0)<6 and (y1-y0)<3
rus=next(f for f in MAP['features'] if f['properties'].get('iso3')=='RUS')
ukr=next(f for f in MAP['features'] if f['properties'].get('iso3')=='UKR')
assert rus['geometry']['type']=='MultiPolygon'
crimea=[sp for sp in rus['geometry']['coordinates'] if is_crimea(sp)]
assert len(crimea)<=1, f"matched {len(crimea)} Crimea-like polys — aborting"
if not crimea: print("No Crimea polygon in RUS (already moved)."); sys.exit(0)
crimea=crimea[0]
rus['geometry']['coordinates']=[sp for sp in rus['geometry']['coordinates'] if not is_crimea(sp)]
if ukr['geometry']['type']=='Polygon': ukr['geometry']={'type':'MultiPolygon','coordinates':[ukr['geometry']['coordinates']]}
ukr['geometry']['coordinates'].append(crimea)
if 'bbox' in ukr:
    cx0,cy0,cx1,cy1=bbox(crimea); b=ukr['bbox']
    ukr['bbox']=[min(b[0],cx0),min(b[1],cy0),max(b[2],cx1),max(b[3],cy1)]
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print("OK: Crimea moved from Russia to Ukraine")
