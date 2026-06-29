import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
lines=open(INP,encoding='utf-8').read().split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
META['subnat']['CHN']['exclude']=["Taiwan","Taiwan Province","Taiwan Sheng","\u53f0\u6e7e","\u81fa\u7063"]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
anchor='    if(cfg.extra){ const _have=new Set(gj.features.map(f=>f.properties[cfg.nameProp]));'
if 'cfg.exclude' not in text:
    n=text.count(anchor); assert n==1, f"anchor matched {n}x"
    text=text.replace(anchor,'    if(cfg.exclude) gj.features=gj.features.filter(f=>!cfg.exclude.includes(f.properties[cfg.nameProp]));\n'+anchor)
open(OUT,'w',encoding='utf-8').write(text)
print("OK: Taiwan excluded from China regional drill-down")
