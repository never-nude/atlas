import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'Atlas deferred init' not in text, 'load_perf3 already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
  'function oceanGrid(){ const feats=[],S=4,EW=180-1e-4;',
  'function oceanGrid(){ const feats=[],S=6,EW=180-1e-4;',
  'ocean-coarsen')
OLD='''  map.addLayer({id:"topo",type:"raster",source:"topo",layout:{visibility:"none"},
    paint:{"raster-opacity":1,"raster-fade-duration":300}}, "fills");

  // sun-driven day/night on the globe — fine grid keeps the terminator smooth (no faceting)
  map.addSource("sunshade",{type:"geojson",data:sunGrid()});
  map.addLayer({id:"sunshade",type:"fill",source:"sunshade",
    paint:{"fill-color":"#02040a","fill-opacity":["coalesce",["get","op"],0],"fill-opacity-transition":{duration:1500}}});

  map.addLayer({id:"hover",type:"line",source:"world",
    paint:{"line-color":"#ffffff","line-width":1.6,"line-blur":0.4},filter:["==","iso3",""]});

  addFlowLayers();
  wireInteractions();
  buildLayerUI();
  simEpoch=Date.now(); simDays=0; paused=false; simSpeed=524/1440; solarDate=new Date();   // default = 524× real time
  setLayer("religion");   // default opening layer = Religion (static choropleth — fast, reliable first paint)
  startSpin();
  initSky();
  wireTimeBar(); updateTimeLabel();
  sizeOrr(); drawOrr();
  { const oh=document.getElementById("orrHead"); if(oh) oh.onclick=()=>document.getElementById("orrInset").classList.toggle("collapsed");
    if(window.innerWidth<=700) document.getElementById("orrInset").classList.add("collapsed"); }   // tidy on phones
  window.addEventListener("resize",()=>{ sizeOrr(); drawOrr(); });
  updateSunShade();    // day/night now advances smoothly inside the master clock loop (startSpin)
  }catch(_e){ console.error("Atlas init error:",_e); }
  finally{ document.getElementById("loading").style.display="none"; }'''
NEW='''  map.addLayer({id:"topo",type:"raster",source:"topo",layout:{visibility:"none"},
    paint:{"raster-opacity":1,"raster-fade-duration":300}}, "fills");

  map.addLayer({id:"hover",type:"line",source:"world",
    paint:{"line-color":"#ffffff","line-width":1.6,"line-blur":0.4},filter:["==","iso3",""]});

  wireInteractions();
  buildLayerUI();
  simEpoch=Date.now(); simDays=0; paused=false; simSpeed=524/1440; solarDate=new Date();   // default = 524× real time
  setLayer("religion");   // default opening layer = Religion (static choropleth — fast, reliable first paint)
  startSpin();
  wireTimeBar(); updateTimeLabel();
  document.getElementById("loading").style.display="none";

  requestAnimationFrame(()=>{ try{
    map.addSource("sunshade",{type:"geojson",data:sunGrid()});
    map.addLayer({id:"sunshade",type:"fill",source:"sunshade",
      paint:{"fill-color":"#02040a","fill-opacity":["coalesce",["get","op"],0],"fill-opacity-transition":{duration:1500}}}, "hover");
    updateSunShade();
    addFlowLayers();
    initSky();
    sizeOrr(); drawOrr();
    { const oh=document.getElementById("orrHead"); if(oh) oh.onclick=()=>document.getElementById("orrInset").classList.toggle("collapsed");
      if(window.innerWidth<=700) document.getElementById("orrInset").classList.add("collapsed"); }
    window.addEventListener("resize",()=>{ sizeOrr(); drawOrr(); });
  }catch(e2){ console.error("Atlas deferred init:",e2); } });
  }catch(_e){ console.error("Atlas init error:",_e); }
  finally{ document.getElementById("loading").style.display="none"; }'''
text=patch(text,OLD,NEW,'load-reorder')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: load handler reordered (globe-first); ocean grid coarsened 4 to 6 deg")
