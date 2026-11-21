#!/usr/bin/env python3
"""Local OSM pedestrian-geometry preference PoC. No OSM or topology edits.
Default exact-endpoint result stays incomplete; snapped routes are review candidates.
"""
import argparse,collections,datetime,hashlib,heapq,json,math,pathlib,xml.etree.ElementTree as ET
import poc
ROOT=pathlib.Path(__file__).resolve().parent
EPS=1e-8

def geometry_class(t):
 if t['highway'] in poc.PED:return 'dedicated_pedestrian'
 if t.get('foot') in poc.ALLOW:return 'road_explicit_foot'
 return 'road_inferred_foot'

def route_search(g,nodes,ways,start,target,multipliers,astar=True,banned=frozenset()):
 """Lexicographically minimize (policy cost, physical distance), no fake edges.
 All edge factors >=1. Haversine is admissible for policy cost. Continue through
 equal lower bounds after reaching target to settle physical-distance ties.
 """
 if start not in g or target not in g:return None
 if any(v<1 or not math.isfinite(v) for v in multipliers.values()):raise ValueError('All multipliers must be finite and >= 1')
 h=lambda n:poc.hav(nodes[n][0],nodes[target][0]) if astar else 0.
 q=[(h(start),0.,0.,start)];labels={start:(0.,0.)};prev={};expanded=0
 while q:
  f,cost,dist,a=heapq.heappop(q)
  if labels.get(a)!=(cost,dist):continue
  if target in labels and f>labels[target][0]+EPS:break
  expanded+=1
  if a==target:continue
  for b,d,w in g[a]:
   if w in banned:continue
   ec=d*multipliers[geometry_class(ways[w][1])]; nc,nd=cost+ec,dist+d
   old=labels.get(b,(math.inf,math.inf))
   if nc<old[0]-EPS or (abs(nc-old[0])<=EPS and nd<old[1]-EPS):
    labels[b]=(nc,nd);prev[b]=(a,w,d,ec);heapq.heappush(q,(nc+h(b),nc,nd,b))
 if target not in labels:return None
 path=[];a=target
 while a!=start:
  b,w,d,ec=prev[a];path.append({'from':b,'to':a,'way':w,'distance_m':d,'policy_cost':ec,'class':geometry_class(ways[w][1])});a=b
 path.reverse()
 return {'policy_cost':labels[target][0],'distance_m':labels[target][1],'segments':path,'expanded':expanded}

def closest_segment(point,nodes,ways,eligible_way_ids):
 """Projection is an endpoint candidate, not a traversable graph edge."""
 lat,lon=point;scale_x=math.pi/180*6371008.8*math.cos(math.radians(lat));scale_y=math.pi/180*6371008.8
 best=None
 for w in eligible_way_ids:
  ids,t=ways[w]
  for a,b in zip(ids,ids[1:]):
   if a not in nodes or b not in nodes:continue
   ay,ax=nodes[a][0];by,bx=nodes[b][0];x1,y1=(ax-lon)*scale_x,(ay-lat)*scale_y;x2,y2=(bx-lon)*scale_x,(by-lat)*scale_y
   dx,dy=x2-x1,y2-y1;den=dx*dx+dy*dy;u=max(0,min(1,-(x1*dx+y1*dy)/den)) if den else 0
   px,py=x1+u*dx,y1+u*dy;proj=(lat+py/scale_y,lon+px/scale_x);d=poc.hav(point,proj)
   v={'way':w,'segment_from_node':a,'segment_to_node':b,'fraction':u,'coordinates_lat_lon':proj,'distance_m':d}
   if best is None or d<best['distance_m']:best=v
 return best

def point_in_polygon(point,coords):
 y,x=point;inside=False
 for (b,a),(d,c) in zip(coords,coords[1:]):
  if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:inside=not inside
 return inside

def summarize(route,ways,nodes):
 if route is None:return None
 out={k:v for k,v in route.items() if k!='segments'};out['segments']=route['segments'];cs=collections.defaultdict(float)
 for e in route['segments']:cs[e['class']]+=e['distance_m']
 out['geometry_distance_m']=dict(cs);out['geometry_share_percent']={c:d/out['distance_m']*100 for c,d in cs.items()}
 out['way_ids']=list(dict.fromkeys(e['way'] for e in route['segments']))
 ids=[route['segments'][0]['from']]+[e['to'] for e in route['segments']] if route['segments'] else []
 out['crossing_nodes']=[{'node':n,'coordinates_lat_lon':nodes[n][0],'tags':nodes[n][1]} for n in ids if nodes[n][1].get('highway')=='crossing']
 out['bridge_way_ids']=[w for w in out['way_ids'] if ways[w][1].get('bridge')=='yes']
 out['status']='review_candidate_route_incomplete'
 out['facility_safety_scored']=False
 return out

def validate_route_provenance(route,ways):
 for e in route['segments']:
  if e['way'] not in ways:raise ValueError('Synthetic or unknown way ID')
  ids=ways[e['way']][0]
  if not any((a==e['from'] and b==e['to']) or (b==e['from'] and a==e['to']) for a,b in zip(ids,ids[1:])):
   raise ValueError('Edge is not an original consecutive OSM node pair')
 return True

def validate_candidate_provenance(candidate,nodes,ways):
 source=candidate['source_osm_ids'];node_ids=source.get('nodes',[])
 if any(n not in nodes for n in node_ids):raise ValueError('Unknown candidate node provenance')
 for w in source.get('ways',[]):
  if w not in ways:raise ValueError('Unknown candidate way provenance')
  if node_ids and not set(ways[w][0]).intersection(node_ids):raise ValueError('Candidate way is not incident to any cited node')
 if candidate['added_to_graph'] or candidate['accepted']:raise ValueError('Unverified review candidate cannot be accepted or added')
 return True

def analyze(foot_multiplier=2.,inferred_multiplier=4.):
 raw=(ROOT/'raw.osm').read_bytes();xml=ET.fromstring(raw)
 nodes={int(e.attrib['id']):((float(e.attrib['lat']),float(e.attrib['lon'])),poc.tags(e)) for e in xml.findall('node')}
 ways={int(e.attrib['id']):([int(n.attrib['ref']) for n in e.findall('nd')],poc.tags(e)) for e in xml.findall('way')}
 g,counts,skips=poc.build(nodes,ways,'inferred');eg,_,_=poc.build(nodes,ways,'explicit');ec,esizes=poc.components(eg)
 s=poc.START;dest=poc.DEST;snap=min(g,key=lambda n:poc.hav(nodes[n][0],nodes[dest][0]));s_snap=min(eg,key=lambda n:poc.hav(nodes[n][0],nodes[s][0]))
 multipliers={'dedicated_pedestrian':1.,'road_explicit_foot':foot_multiplier,'road_inferred_foot':inferred_multiplier}
 if any(v<1 or not math.isfinite(v) for v in multipliers.values()):raise ValueError('All multipliers must be finite and >= 1')
 res={'version':2,'run_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_url':poc.URL,'acquisition':json.loads((ROOT/'acquisition.json').read_text()),'raw_sha256':hashlib.sha256(raw).hexdigest(),'status':'route_incomplete','exact_route':None,'verified_complete_walking_route':False,'topology_edits_applied':0,'simulated_connectors_enabled':False,'safety_scored':False,'start':{'node':s,'coordinates_lat_lon':nodes[s][0],'basis':'outside endpoint of mapped 기숙사-옆문 도보, not a tagged gate','exact_node_in_inferred_graph':s in g},'destination':{'node':dest,'coordinates_lat_lon':nodes[dest][0],'tags':nodes[dest][1],'exact_node_in_graph':dest in g,'snap_node':snap,'snap_coordinates_lat_lon':nodes[snap][0],'snap_gap_m':poc.hav(nodes[dest][0],nodes[snap][0]),'connector_verified':False},'policy':{'name_ko':'보행선 우선 / 데이터 확실성 페널티','formula':'sum(physical distance × geometry-class multiplier); tie: shorter physical distance','multipliers':multipliers,'weights_empirically_calibrated':False,'heuristic':'haversine distance, admissible because each cost >= physical distance'},'graph':{'vertices':len(g),'directed_edges':sum(map(len,g.values())),'accepted_way_counts':counts,'skipped_segments':skips},'explicit_diagnosis':{'source_snap_node':s_snap,'source_snap_gap_m':poc.hav(nodes[s][0],nodes[s_snap][0]),'source_component_size':sum(c==ec[s_snap] for c in ec.values()),'station_nearby_component_size':sum(c==ec[snap] for c in ec.values()),'same_component':ec[s_snap]==ec[snap],'components':len(esizes)},'routes':{},'sensitivity':[],'corrections':[]}
 pedways=[w for w,(ids,t) in ways.items() if t.get('highway') in poc.PED and t.get('area')!='yes']
 incident=collections.defaultdict(list)
 for w,(ids,t) in ways.items():
  if t.get('highway'):
   for n in ids:incident[n].append(w)
 pednodes={n for w in pedways for n in ways[w][0] if n in nodes}
 nearest_ped_node=min(pednodes,key=lambda n:poc.hav(nodes[n][0],nodes[s][0]))
 res['explicit_diagnosis']['source_snap_incident_highway_ways']=[{'way':w,'tags':ways[w][1],'geometry_class':geometry_class(ways[w][1])} for w in incident[s_snap]]
 res['explicit_diagnosis']['nearest_dedicated_pedestrian_node']={'node':nearest_ped_node,'coordinates_lat_lon':nodes[nearest_ped_node][0],'distance_m':poc.hav(nodes[s][0],nodes[nearest_ped_node][0]),'incident_way_ids':incident[nearest_ped_node],'added_to_graph':False}
 res['destination']['nearest_pedestrian_segment_candidate']=closest_segment(nodes[dest][0],nodes,ways,pedways)
 policies={'distance_only':{'dedicated_pedestrian':1.,'road_explicit_foot':1.,'road_inferred_foot':1.},'moderate_pedestrian_preferred':{'dedicated_pedestrian':1.,'road_explicit_foot':1.5,'road_inferred_foot':3.},'pedestrian_preferred':multipliers}
 for name,m in policies.items():
  a=route_search(g,nodes,ways,s,snap,m);d=route_search(g,nodes,ways,s,snap,m,False)
  assert a and d and abs(a['policy_cost']-d['policy_cost'])<1e-6 and abs(a['distance_m']-d['distance_m'])<1e-6
  out=summarize(a,ways,nodes);out['dijkstra_policy_cost']=d['policy_cost'];out['dijkstra_distance_m']=d['distance_m'];out['dijkstra_expanded']=d['expanded'];res['routes'][name]=out
 # third candidate is the previous explicit primary/secondary exclusion policy; not a safety recommendation.
 ng,_,_=poc.build(nodes,ways,'no_major');a=route_search(ng,nodes,ways,s,snap,policies['distance_only']);d=route_search(ng,nodes,ways,s,snap,policies['distance_only'],False)
 assert abs(a['policy_cost']-d['policy_cost'])<1e-6
 res['routes']['primary_secondary_excluded']=summarize(a,ways,nodes)
 for x,y in [(1,1),(1.5,3),(2,4),(4,12),(10,30)]:
  mm={'dedicated_pedestrian':1.,'road_explicit_foot':x,'road_inferred_foot':y};a=route_search(g,nodes,ways,s,snap,mm);d=route_search(g,nodes,ways,s,snap,mm,False)
  assert abs(a['policy_cost']-d['policy_cost'])<1e-6 and abs(a['distance_m']-d['distance_m'])<1e-6
  sm=summarize(a,ways,nodes);res['sensitivity'].append({'multipliers':mm,'policy_cost':a['policy_cost'],'distance_m':a['distance_m'],'pedestrian_share_percent':sm['geometry_share_percent'].get('dedicated_pedestrian',0),'way_ids':sm['way_ids'],'dijkstra_match':True})
 res['internal_campus_test']={}
 for name,m in policies.items():
  a=route_search(g,nodes,ways,9799703963,snap,m)
  sm=summarize(a,ways,nodes)
  res['internal_campus_test'][name]={'start_node':9799703963,'coordinates_lat_lon':nodes[9799703963][0],'distance_m':a['distance_m'],'policy_cost':a['policy_cost'],'complete':False,'way_ids':sm['way_ids'],'geometry_distance_m':sm['geometry_distance_m'],'geometry_share_percent':sm['geometry_share_percent']}
 base_edges={(e['from'],e['to'],e['way']) for e in res['routes']['distance_only']['segments']}
 for name,route in res['routes'].items():
  shared=sum(e['distance_m'] for e in route['segments'] if (e['from'],e['to'],e['way']) in base_edges)
  route['shared_with_distance_only_m']=shared;route['shared_percent_of_distance_only']=shared/res['routes']['distance_only']['distance_m']*100
 # All candidate geometry has explicit status and provenance. These are REVIEW items, never inserted edges.
 def candidate(cid,kind,coords,reason,source_ids,**extra):
  item={'id':cid,'kind':kind,'status':'unverified_review_candidate','accepted':False,'added_to_graph':False,'coordinates_lat_lon':coords,'reason_ko':reason,'source_osm_ids':source_ids,'verification_needed_ko':'현장/공식 시설도면으로 실제 보도·횡단·접근 가능 여부 및 장애물·운영시간 확인',**extra};res['corrections'].append(item);return item
 candidate('station-exit-gap','missing_endpoint_connector',[nodes[snap][0],nodes[dest][0]],'출구 노드가 어떤 highway way에도 없으며, 가까운 횡단보도 노드와12.56m 이격. 단순 근접은 연결 근거가 아니다. 검증 전 edge를 추가하지 않는다.',{'nodes':[snap,dest],'ways':[472303067]},gap_m=poc.hav(nodes[snap][0],nodes[dest][0]))
 proj=res['destination']['nearest_pedestrian_segment_candidate']
 if 0<proj['fraction']<1:
  candidate('station-segment-snap','projection_only',[nodes[dest][0],proj['coordinates_lat_lon']],'보행선으로의 기하학적 투영 후보. projection point는 OSM node가 아니고 connector도 입증되지 않았다.',{'nodes':[dest,proj['segment_from_node'],proj['segment_to_node']],'ways':[proj['way']]},gap_m=proj['distance_m'],projection_fraction=proj['fraction'])
 candidate('side-door-explicit-access-gap','origin_access_review',[nodes[s][0],nodes[s_snap][0]],'옆문 도보(service) 바깥 endpoint와 명시 foot=yes 도로노드는 서로 다른 node ID. 근접11.30m를 자동 연결하지 않는다. 이 대상은 전용 footway가 아니다.',{'nodes':[s,s_snap],'ways':sorted(set(incident[s]+incident[s_snap]))},gap_m=poc.hav(nodes[s][0],nodes[s_snap][0]),target_geometry_class='road_explicit_foot')
 sc={n for n,c in ec.items() if c==ec[s_snap]};tc={n for n,c in ec.items() if c==ec[snap]}
 gap,a,b=min((poc.hav(nodes[a][0],nodes[b][0]),a,b) for a in sc for b in tc)
 candidate('explicit-component-nearest-gap','component_gap_review',[nodes[a][0],nodes[b][0]],'출발·역 explicit 성분 사이의 가장 가까운 node 쌍. 직선은 관측 경로가 아니며 연결을 허용하지 않는다.',{'nodes':[a,b]},gap_m=gap)
 # Identify road runs of preferred route as concrete sidewalk/crossing verification priorities.
 runs=[]
 for e in res['routes']['pedestrian_preferred']['segments']:
  if not runs or runs[-1]['class']!=e['class']:runs.append({'class':e['class'],'segments':[]})
  runs[-1]['segments'].append(e)
 res['preferred_route_runs']=[]
 for i,run in enumerate(runs):
  ee=run['segments'];a,b=ee[0]['from'],ee[-1]['to'];wid=list(dict.fromkeys(e['way'] for e in ee));dist=sum(e['distance_m'] for e in ee)
  res['preferred_route_runs'].append({'class':run['class'],'from_node':a,'to_node':b,'distance_m':dist,'way_ids':wid})
  if run['class']!='dedicated_pedestrian':
   coords=[nodes[a][0]]+[nodes[e['to']][0] for e in ee]
   candidate('road-run-'+str(i),'sidewalk_geometry_review',coords,'원본 도로 선형으로만 연결된 구간. 실제 보도의 위치·연속성과 횡단 topology를 확인할 우선 검토 대상이며 도로 중심선 offset은 생성하지 않는다.',{'nodes':[a]+[e['to'] for e in ee],'ways':wid},distance_m=dist,geometry_class=run['class'])
 # Named walking-purpose service ways are ambiguous classification, not proof of legal access or sidewalk geometry.
 named=[]
 for w,(ids,t) in ways.items():
  if t.get('highway')=='service' and ('도보' in t.get('name','') or '보도' in t.get('name','')):
   named.append({'way':w,'tags':t,'status':'unverified_classification_review','automatically_reclassified':False})
 res['named_service_walkway_candidates']=named
 areas=[]
 for w,(ids,t) in ways.items():
  if t.get('highway')=='pedestrian' and t.get('area')=='yes':
   coords=[nodes[n][0] for n in ids];shared=sorted({n for n in ids if n in eg})
   areas.append({'way':w,'tags':t,'contains_station_exit':point_in_polygon(nodes[dest][0],coords),'shared_linear_graph_nodes':shared,'used_for_station_connector':False})
 res['pedestrian_area_audit']=areas
 # audit exact edge provenance and untouched snapshot
 for route in res['routes'].values():
  validate_route_provenance(route,ways)
 for item in res['corrections']:validate_candidate_provenance(item,nodes,ways)
 res['edge_provenance_verified']=True
 res['independent_validation_note']='Parent independently reproduced baseline 2/4 policy with SciPy sparse csgraph Dijkstra: policy cost2975.4893480921746, physical distance1932.5627727980034m; all adjacency derives from raw consecutive OSM nodes.'
 features=[]
 for name,route in res['routes'].items():
  for e in route['segments']:features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[list(reversed(nodes[e['from']][0])),list(reversed(nodes[e['to']][0]))]},'properties':{'route':name,'status':route['status'],**e,**ways[e['way']][1]}})
 corrections={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'LineString','coordinates':[list(reversed(c)) for c in item['coordinates_lat_lon']]},'properties':{k:v for k,v in item.items() if k!='coordinates_lat_lon'}} for item in res['corrections']]}
 (ROOT/'result-v2.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));(ROOT/'routes-v2.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2));(ROOT/'correction-candidates.geojson').write_text(json.dumps(corrections,ensure_ascii=False,indent=2));(ROOT/'correction-candidates.json').write_text(json.dumps(res['corrections'],ensure_ascii=False,indent=2))
 return res
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--foot-road-multiplier',type=float,default=2);ap.add_argument('--inferred-road-multiplier',type=float,default=4);args=ap.parse_args();r=analyze(args.foot_road_multiplier,args.inferred_road_multiplier)
 print(json.dumps({'status':r['status'],'topology_edits_applied':r['topology_edits_applied'],'routes':{n:{k:v[k] for k in ['policy_cost','distance_m','geometry_distance_m','geometry_share_percent','shared_percent_of_distance_only']} for n,v in r['routes'].items()},'review_candidates':len(r['corrections'])},ensure_ascii=False,indent=2))
