#!/usr/bin/env python3
"""Stdlib OSM walking-connectivity PoC. No geometric joins or invented links.
Usage: python poc.py [--download]; raw.osm is the immutable input snapshot.
"""
import argparse, collections, datetime, hashlib, heapq, json, math, pathlib, urllib.request, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent
URL = 'https://www.openstreetmap.org/api/0.6/map?bbox=126.719,37.334,126.751,37.359'
START = 9799703999  # endpoint of mapped 기숙사-옆문 도보, not a tagged gate
DEST = 3403277121
ALLOW = {'yes','designated','official','permissive'}
DENY = {'no','private','customers','delivery','destination','agricultural','forestry'}
PED = {'footway','pedestrian','steps','path'}
ROADS = {'service','residential','living_street','unclassified','tertiary','tertiary_link','secondary','secondary_link','primary','primary_link','road','track'}
def hav(a,b):
    y1,x1,y2,x2=map(math.radians,(*a,*b)); dy=y2-y1; dx=x2-x1
    return 6371008.8*2*math.asin(min(1,math.sqrt(math.sin(dy/2)**2+math.cos(y1)*math.cos(y2)*math.sin(dx/2)**2)))
def tags(e): return {t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
def permitted(t):
    # Unknown/restricted access is excluded; a specific foot permission overrides access.
    if any('conditional' in k and (k.startswith('foot') or k.startswith('access')) for k in t): return False
    f=t.get('foot'); a=t.get('access')
    if f is not None: return f in ALLOW
    return a is None or a in ALLOW
def accepted(t,mode):
    h=t.get('highway','')
    if not h:return False
    if h in {'motorway','motorway_link','trunk','trunk_link','construction','proposed','raceway'} or t.get('area')=='yes' or not permitted(t): return False
    if t.get('oneway:foot','no') not in {'no','0','false','yes','1','true','-1'}: return False
    if any(t.get(k) not in ALLOW|DENY for k in ['foot:forward','foot:backward'] if k in t): return False
    if t.get('sidewalk')=='separate' and h not in PED and t.get('foot') not in ALLOW: return False
    if mode=='explicit': return h in PED or t.get('foot') in ALLOW
    if mode=='no_major' and h in {'primary','primary_link','secondary','secondary_link'} and t.get('foot') not in ALLOW: return False
    return h in PED|ROADS or t.get('foot') in ALLOW
def blocked(t):
    if not permitted(t): return True
    b=t.get('barrier')
    return b is not None and b not in {'bollard','cycle_barrier','entrance','kerb','cattle_grid'} and t.get('foot') not in ALLOW
def build(nodes,ways,mode):
    g=collections.defaultdict(list); counts=collections.Counter(); skipped=collections.Counter()
    for wid,(ids,t) in ways.items():
        if not accepted(t,mode): continue
        counts[t['highway']]+=1
        for a,b in zip(ids,ids[1:]):
            if a not in nodes or b not in nodes: skipped['missing_node_segments']+=1;continue
            if blocked(nodes[a][1]) or blocked(nodes[b][1]): skipped['blocked_node_segments']+=1;continue
            d=hav(nodes[a][0],nodes[b][0]); on=t.get('oneway:foot','no')
            if on not in {'-1'} and t.get('foot:forward') not in DENY:g[a].append((b,d,wid))
            if on not in {'yes','1','true'} and t.get('foot:backward') not in DENY:g[b].append((a,d,wid))
            # vehicle oneway intentionally does not constrain pedestrians.
            g[a];g[b]
    return dict(g),dict(counts),dict(skipped)
def components(g):
    und=collections.defaultdict(set)
    for a,ee in g.items():
        for b,_,_ in ee:und[a].add(b);und[b].add(a)
    comp={};sizes=[]
    for s in g:
        if s in comp:continue
        ci=len(sizes);q=[s];comp[s]=ci;size=0
        while q:
            a=q.pop();size+=1
            for b in und[a]:
                if b not in comp:comp[b]=ci;q.append(b)
        sizes.append(size)
    return comp,sorted(sizes,reverse=True)
def shortest(g,nodes,s,t,astar=True,banned=frozenset()):
    h=lambda a:hav(nodes[a][0],nodes[t][0]) if astar else 0
    q=[(h(s),0,s)];dist={s:0};prev={};expanded=0
    while q:
        _,d,a=heapq.heappop(q)
        if d>dist[a]+1e-9:continue
        expanded+=1
        if a==t:
            path=[]
            while a!=s:
                b,w,dd=prev[a];path.append((b,a,w,dd));a=b
            return d,list(reversed(path)),expanded
        for b,dd,w in g.get(a,[]):
            if w in banned:continue
            nd=d+dd
            if nd<dist.get(b,math.inf):dist[b]=nd;prev[b]=(a,w,dd);heapq.heappush(q,(nd+h(b),nd,b))
    return None,[],expanded
def run():
    ap=argparse.ArgumentParser();ap.add_argument('--download',action='store_true');args=ap.parse_args()
    if args.download:
        with urllib.request.urlopen(URL,timeout=90) as r:(ROOT/'raw.osm').write_bytes(r.read())
        (ROOT/'acquisition.json').write_text(json.dumps({'source_url':URL,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    data=(ROOT/'raw.osm').read_bytes();r=ET.fromstring(data)
    nodes={int(e.attrib['id']):((float(e.attrib['lat']),float(e.attrib['lon'])),tags(e)) for e in r.findall('node')}
    ways={int(e.attrib['id']):([int(n.attrib['ref']) for n in e.findall('nd')],tags(e)) for e in r.findall('way')}
    acquisition=json.loads((ROOT/'acquisition.json').read_text())
    result={'source_url':URL,'acquisition':acquisition,'run_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'counts':dict(collections.Counter(e.tag for e in r)), 'start':{'node':START,'coordinates_lat_lon':nodes[START][0],'basis':'mapped way 1067311761 기숙사-옆문 도보 outside endpoint; not explicit gate'},'destination':{'node':DEST,'coordinates_lat_lon':nodes[DEST][0],'tags':nodes[DEST][1]},'university':{'way':234844934,'tags':ways[234844934][1],'previous_coordinate_lat_lon':[37.34278,126.72861],'previous_coordinate_inside_campus':False},'modes':{}}
    features=[]
    for mode in ['explicit','no_major','inferred']:
        g,counts,skipped=build(nodes,ways,mode);comp,sizes=components(g)
        snaps={k:min(g,key=lambda n:hav(nodes[n][0],nodes[v][0])) for k,v in [('start',START),('destination',DEST)]}
        sd={k:hav(nodes[snaps[k]][0],nodes[v][0]) for k,v in [('start',START),('destination',DEST)]}
        s,t=snaps['start'],snaps['destination'];d,path,ex=shortest(g,nodes,s,t);dd,_,dex=shortest(g,nodes,s,t,False)
        assert (d is None)==(dd is None) and (d is None or abs(d-dd)<1e-6)
        m={'vertices':len(g),'directed_edges':sum(map(len,g.values())),'accepted_highway_way_counts':counts,'skipped_segments':skipped,'weak_components':len(sizes),'largest_component_sizes':sizes[:10],'snap_nodes':snaps,'snap_distance_m':sd,'same_weak_component':comp[s]==comp[t],'distance_m':d,'astar_expanded':ex,'dijkstra_expanded':dex,'dijkstra_distance_m':dd,'exact_requested_nodes_in_graph':{'start':START in g,'destination':DEST in g},'route_ways':[],'route_node_ids':[s]+[b for _,b,_,_ in path]}
        wc=collections.defaultdict(float)
        for _,_,w,ed in path:wc[w]+=ed
        m['route_ways']=[{'way':w,'distance_m':v,'tags':ways[w][1]} for w,v in wc.items()]
        classes=collections.defaultdict(float)
        for w,v in wc.items():
            wt=ways[w][1]
            c='dedicated_pedestrian_geometry' if wt['highway'] in PED else ('road_geometry_explicit_foot' if wt.get('foot') in ALLOW else 'road_geometry_inferred_foot')
            classes[c]+=v
        m['route_geometry_distance_m']=dict(classes)
        m['route_geometry_share_percent']={k:v/d*100 for k,v in classes.items()} if d else {}
        m['internal_campus_start_test']={}
        campus_start=9799703963
        if campus_start in g:
            cd,cp,_=shortest(g,nodes,campus_start,t)
            m['internal_campus_start_test']={'node':campus_start,'coordinates_lat_lon':nodes[campus_start][0],'distance_m':cd,'route_way_ids':list(dict.fromkeys(w for _,_,w,_ in cp))}
        else:m['internal_campus_start_test']={'node':campus_start,'in_graph':False,'distance_m':None}
        m['crossing_nodes']=[{'node':n,'tags':nodes[n][1]} for n in m['route_node_ids'] if nodes[n][1].get('highway')=='crossing' or 'crossing' in nodes[n][1]]
        m['primary_secondary_distance_m']=sum(v for w,v in wc.items() if ways[w][1].get('highway') in {'primary','primary_link','secondary','secondary_link'})
        m['alternative_excluding_major_route_ways']=None
        major={w for w in wc if ways[w][1].get('highway') in {'primary','primary_link','secondary','secondary_link'}}
        if major:
            ad,apath,_=shortest(g,nodes,s,t,banned=major);m['alternative_excluding_major_route_ways']={'excluded_way_ids':sorted(major),'distance_m':ad,'route_way_ids':list(dict.fromkeys(w for _,_,w,_ in apath))}
            alt_edges={(a,b,w) for a,b,w,_ in apath}
            shared=sum(ed for a,b,w,ed in path if (a,b,w) in alt_edges)
            m['alternative_excluding_major_route_ways'].update({'shared_directed_edge_distance_m':shared,'shared_percent_of_shortest':100*shared/d if d else None,'safety_scored':False})
        result['modes'][mode]=m
        for a,b,w,ed in path:features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[list(reversed(nodes[a][0])),list(reversed(nodes[b][0]))]},'properties':{'mode':mode,'way':w,'from_node':a,'to_node':b,'distance_m':ed,**ways[w][1]}})
    (ROOT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (ROOT/'route.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2))
    restrictions=[{'id':e.attrib['id'],'tags':tags(e)} for e in r.findall('relation') if tags(e).get('type')=='restriction']
    result['restriction_relation_audit']=restrictions
    result['raw_highway_way_counts']=dict(collections.Counter(t['highway'] for _,t in ways.values() if 'highway' in t))
    result['raw_crossing_node_count']=sum(t.get('highway')=='crossing' for _,t in nodes.values())
    result['all_road_geometry_route_nodes_mixed_level']={}
    for mode,m in result['modes'].items():
        incident=collections.defaultdict(set)
        for wid,(ids,wt) in ways.items():
            if accepted(wt,mode):
                level=(wt.get('layer','0'),wt.get('bridge','no'),wt.get('tunnel','no'))
                for n in ids:incident[n].add(level)
        result['all_road_geometry_route_nodes_mixed_level'][mode]=[{'node':n,'incident_levels':sorted(incident[n])} for n in m['route_node_ids'] if len(incident[n])>1]
    (ROOT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:{kk:v[kk] for kk in ['vertices','directed_edges','weak_components','snap_nodes','snap_distance_m','distance_m','primary_secondary_distance_m','astar_expanded','dijkstra_expanded']} for k,v in result['modes'].items()},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
