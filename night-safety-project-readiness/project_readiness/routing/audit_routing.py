"""Read-only snapshot audit: no topology changes, connectors or facility score."""
import sys,json,hashlib,collections,heapq,itertools,pathlib,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
SRC=ROOT.parent.parent/'osm_poc_v2';sys.path.insert(0,str(SRC))
import poc,poc_v2
raw=(SRC/'raw.osm').read_bytes();xml=ET.fromstring(raw)
nodes={int(e.attrib['id']):((float(e.attrib['lat']),float(e.attrib['lon'])),poc.tags(e)) for e in xml.findall('node')}
ways={int(e.attrib['id']):([int(x.attrib['ref']) for x in e.findall('nd')],poc.tags(e)) for e in xml.findall('way')}
inc=collections.defaultdict(list)
for w,(ids,t) in ways.items():
 for n in ids:inc[n].append(w)
poly=[nodes[n][0] for n in ways[234844934][0]]
boundary=[]
for w,(ids,t) in ways.items():
 if 'highway' not in t:continue
 inside=[poc_v2.point_in_polygon(nodes[n][0],poly) for n in ids]
 for a,b,ia,ib in zip(ids,ids[1:],inside,inside[1:]):
  if ia!=ib:boundary.append({'way':w,'tags':t,'inside_node':a if ia else b,'outside_node':b if ia else a,'gate_verified':False})
origins=[x['outside_node'] for x in boundary]+[9799703963]
targets=[4665188383,4665188380,4673861122,3403277121,3403277120]
pol={'dedicated_pedestrian':1.,'road_explicit_foot':2.,'road_inferred_foot':4.}
result={'raw_sha256':hashlib.sha256(raw).hexdigest(),'original_edges_only':True,'physical_verification':False,'campus_boundary_crossing_ways':boundary,'targets':[{ 'node':n,'lat_lon':nodes[n][0],'tags':nodes[n][1]} for n in targets],'modes':{},'routes':[]}
features=[]
graphs={m:poc.build(nodes,ways,m)[0] for m in ['inferred','no_major','explicit']}
graphs['no_steps_bridge']={a:[e for e in ee if ways[e[2]][1].get('highway')!='steps' and ways[e[2]][1].get('bridge')!='yes'] for a,ee in graphs['inferred'].items()}
graphs['no_untagged_access']={a:[e for e in ee if ways[e[2]][1].get('foot') in poc.ALLOW or ways[e[2]][1].get('access') in poc.ALLOW] for a,ee in graphs['inferred'].items()}
for mode,g in graphs.items():
 asym=[(a,b,w) for a,ee in g.items() for b,d,w in ee if not any(bb==a and ww==w for bb,dd,ww in g.get(b,[]))]
 successes=0;reverse_successes=0
 for s,t in itertools.product(origins,targets):
  r=poc_v2.route_search(g,nodes,ways,s,t,pol);back=poc_v2.route_search(g,nodes,ways,t,s,pol)
  successes+=bool(r);reverse_successes+=bool(back)
  row={'mode':mode,'from_node':s,'to_node':t,'graph_reachable':bool(r),'reverse_reachable':bool(back),'distance_m':r['distance_m'] if r else None,'status':'graph_only_unverified_physical_route','verified_complete_walking_route':False,'facility_safety_scored':False}
  if r:
   d=poc_v2.route_search(g,nodes,ways,s,t,pol,False)
   assert abs(d['policy_cost']-r['policy_cost'])<1e-6
   assert poc_v2.validate_route_provenance(r,ways)
   row['astar_dijkstra_cost_match']=True;row['way_ids']=list(dict.fromkeys(e['way'] for e in r['segments']))
   row['steps_ways']=[w for w in row['way_ids'] if ways[w][1].get('highway')=='steps'];row['bridge_ways']=[w for w in row['way_ids'] if ways[w][1].get('bridge')=='yes']
   if mode=='inferred' and t==4665188383:
    coords=[nodes[s][0]]+[nodes[e['to']][0] for e in r['segments']]
    features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[list(reversed(c)) for c in coords]},'properties':row.copy()})
  result['routes'].append(row)
 result['modes'][mode]={'vertices':len(g),'directed_edges':sum(map(len,g.values())),'asymmetric_edges':len(asym),'forward_reachable_pairs':successes,'reverse_reachable_pairs':reverse_successes,'tested_pairs':len(origins)*len(targets)}
base=json.loads((SRC/'result-v2.json').read_text())['routes']['pedestrian_preferred']
pathnodes=[base['segments'][0]['from']]+[e['to'] for e in base['segments']]
result['preferred_route_hazards']={'crossings':[{ 'node':n,'tags':nodes[n][1],'incident_highways':[{'way':w,'tags':ways[w][1]} for w in inc[n] if 'highway' in ways[w][1]]} for n in pathnodes if nodes[n][1].get('highway')=='crossing'],'steps':[{ 'way':w,'tags':ways[w][1]} for w in base['way_ids'] if ways[w][1].get('highway')=='steps'],'bridges':[{ 'way':w,'tags':ways[w][1]} for w in base['way_ids'] if ways[w][1].get('bridge')=='yes'],'conditional_or_opening_hours':[{ 'way':w,'tags':ways[w][1]} for w in base['way_ids'] if any('conditional' in k or k=='opening_hours' for k in ways[w][1])]}
result['candidate_audit']=[]
for c in json.loads((SRC/'correction-candidates.json').read_text()):
 ids=c['source_osm_ids'];result['candidate_audit'].append({'id':c['id'],'correction_supported':False,'nodes':[{ 'id':n,'tags':nodes[n][1],'incident_highways':[{'way':w,'tags':ways[w][1]} for w in inc[n] if 'highway' in ways[w][1]]} for n in ids.get('nodes',[])],'way_tags':[{'way':w,'tags':ways[w][1]} for w in ids.get('ways',[])]})
# Yen loopless paths on the original directed multiedges (no dependency required).
g=graphs['inferred'];s=9799703999;t=4665188383
def shortest(start,ban_nodes=set(),ban_edges=set()):
 q=[(0.,start)];cost={start:0.};prev={}
 while q:
  d,a=heapq.heappop(q)
  if d!=cost.get(a):continue
  if a==t:
   out=[]
   while a!=start:b,dd,w=prev[a];out.append((b,a,w,dd));a=b
   return list(reversed(out))
  for b,dd,w in g.get(a,[]):
   if b in ban_nodes or (a,b,w) in ban_edges:continue
   if d+dd<cost.get(b,float('inf')):cost[b]=d+dd;prev[b]=(a,dd,w);heapq.heappush(q,(d+dd,b))
def key(p):return tuple((a,b,w) for a,b,w,d in p)
accepted=[shortest(s)];queue=[];seen={key(accepted[0])};counter=itertools.count()
for _ in range(29):
 last=accepted[-1]
 for i in range(len(last)):
  root=last[:i];rn=[s]+[e[1] for e in root];spur=rn[-1]
  bans={(p[i][0],p[i][1],p[i][2]) for p in accepted if len(p)>i and key(p[:i])==key(root)}
  tail=shortest(spur,set(rn[:-1]),bans)
  if tail is None:continue
  cand=root+tail;k=key(cand)
  if k not in seen:seen.add(k);heapq.heappush(queue,(sum(e[3] for e in cand),next(counter),cand))
 if not queue:break
 accepted.append(heapq.heappop(queue)[2])
shortdistance=sum(e[3] for e in accepted[0]);baseedges=set(key(accepted[0]));ks=[]
for i,p in enumerate(accepted):
 pn=[s]+[e[1] for e in p]
 assert len(pn)==len(set(pn)) and pn[-1]==t
 assert all(any(b==bb and w==ww and abs(d-dd)<1e-8 for bb,dd,ww in g[a]) for a,b,w,d in p)
 d=sum(e[3] for e in p);shared=sum(e[3] for e in p if (e[0],e[1],e[2]) in baseedges)
 ped=sum(e[3] for e in p if ways[e[2]][1]['highway'] in poc.PED)
 ks.append({'rank':i+1,'distance_m':d,'dedicated_pedestrian_share_percent':ped/d*100,'extra_minutes_at_1_2_mps':(d-shortdistance)/72.,'shared_shortest_m':shared,'shared_fraction_of_shortest':shared/shortdistance,'way_ids':list(dict.fromkeys(e[2] for e in p))})
selected=[]
for i,p in enumerate(accepted):
 if all(sum(e[3] for e in p if (e[0],e[1],e[2]) in set(key(accepted[j])))/min(sum(e[3] for e in p),sum(e[3] for e in accepted[j]))<.8 for j in selected):selected.append(i)
result['pairwise_diversity_greedy_ranks']=[i+1 for i in selected]
result['k_shortest_test']={'algorithm':'Yen loopless, original directed edges; physical distance ordering','k':len(ks),'walking_speed_assumption_mps':1.2,'plus_10_min_limit_distance_m':shortdistance+720.,'paths':ks,'distinct_way_sequences':len({tuple(x['way_ids']) for x in ks}),'accepted_below_80_percent_shared_and_plus_10min':[x['rank'] for x in ks if x['shared_fraction_of_shortest']<.8 and x['extra_minutes_at_1_2_mps']<=10]}
assert all(a['distance_m']<=b['distance_m']+1e-8 for a,b in zip(ks,ks[1:]))
assert (SRC/'raw.osm').read_bytes()==raw
(ROOT/'routing-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(ROOT/'expanded-routes.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2))
print(json.dumps({'modes':result['modes'],'boundary_crossings':boundary,'hazards':result['preferred_route_hazards'],'k_shortest_test':{k:v for k,v in result['k_shortest_test'].items() if k!='paths'},'k_distance_range_m':[ks[0]['distance_m'],ks[-1]['distance_m']]},ensure_ascii=False,indent=2))
