import unittest,hashlib,pathlib,math
import poc,poc_v2 as v2
class V2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=hashlib.sha256((v2.ROOT/'raw.osm').read_bytes()).hexdigest()
  cls.result=v2.analyze()
 def test_exact_endpoint_incomplete_default(self):
  r=self.result;self.assertEqual(r['status'],'route_incomplete');self.assertIsNone(r['exact_route']);self.assertFalse(r['verified_complete_walking_route']);self.assertFalse(r['destination']['exact_node_in_graph']);self.assertFalse(r['simulated_connectors_enabled'])
 def test_original_snapshot_and_review_only(self):
  self.assertEqual(self.before,hashlib.sha256((v2.ROOT/'raw.osm').read_bytes()).hexdigest())
  self.assertEqual(self.result['topology_edits_applied'],0)
  for c in self.result['corrections']:
   self.assertEqual(c['status'],'unverified_review_candidate');self.assertFalse(c['accepted']);self.assertFalse(c['added_to_graph']);self.assertTrue(c['source_osm_ids']);self.assertTrue(c['verification_needed_ko'])
 def test_illicit_edge_provenance_rejected(self):
  ws={1:([1,2,3],{'highway':'footway'})}
  with self.assertRaises(ValueError):v2.validate_route_provenance({'segments':[{'way':1,'from':1,'to':3}]},ws)
  with self.assertRaises(ValueError):v2.validate_route_provenance({'segments':[{'way':999,'from':1,'to':2}]},ws)
  self.assertTrue(v2.validate_route_provenance({'segments':[{'way':1,'from':2,'to':1}]},ws))
 def test_weighted_cost_optimum_and_dijkstra(self):
  ns={1:((37,126),{}),2:((37,126.001),{}),3:((37.001,126.001),{}),4:((37.001,126.002),{})}
  ws={1:([1,2,4],{'highway':'service'}),2:([1,3,4],{'highway':'footway'})};g,_,_=poc.build(ns,ws,'inferred');mm={'dedicated_pedestrian':1,'road_explicit_foot':2,'road_inferred_foot':4}
  a=v2.route_search(g,ns,ws,1,4,mm);d=v2.route_search(g,ns,ws,1,4,mm,False)
  self.assertAlmostEqual(a['policy_cost'],d['policy_cost']);self.assertTrue(all(e['way']==2 for e in a['segments']))
 def test_cost_tie_prefers_shorter_physical_distance(self):
  ns={n:((0,0),{}) for n in [1,2,3,4]};ws={1:([1,2,4],{'highway':'service'}),2:([1,3,4],{'highway':'footway'})}
  g={1:[(2,1,1),(3,2,2)],2:[(4,1,1)],3:[(4,2,2)],4:[]};mm={'dedicated_pedestrian':1,'road_explicit_foot':2,'road_inferred_foot':2}
  a=v2.route_search(g,ns,ws,1,4,mm);self.assertEqual(a['policy_cost'],4);self.assertEqual(a['distance_m'],2)
 def test_invalid_policy_rejected(self):
  for weight in [.9,float('nan'),float('inf')]:
   with self.assertRaises(ValueError):v2.route_search({1:[],2:[]},{1:((0,0),{}),2:((0,0),{})},{},1,2,{'dedicated_pedestrian':weight})
 def test_segment_projection_does_not_insert_connector(self):
  ns={1:((0,0),{}),2:((0,.002),{})};ws={10:([1,2],{'highway':'footway'})};g,_,_=poc.build(ns,ws,'explicit')
  p=v2.closest_segment((.001,.001),ns,ws,[10]);self.assertAlmostEqual(p['fraction'],.5);self.assertEqual(set(g),{1,2});self.assertEqual(set(ns),{1,2})
 def test_measured_improvement_and_sensitivity(self):
  r=self.result;a=r['routes']['distance_only'];b=r['routes']['pedestrian_preferred']
  self.assertGreater(b['geometry_share_percent']['dedicated_pedestrian'],a['geometry_share_percent']['dedicated_pedestrian']);self.assertGreater(b['distance_m'],a['distance_m'])
  self.assertAlmostEqual(b['policy_cost'],b['dijkstra_policy_cost'],places=6)
  self.assertTrue(all(x['dijkstra_match'] for x in r['sensitivity']))
 def test_origin_nearest_explicit_road_not_footway(self):
  d=self.result['explicit_diagnosis'];self.assertEqual(d['source_snap_node'],4130186271)
  self.assertTrue(all(x['tags']['highway'] not in poc.PED for x in d['source_snap_incident_highway_ways']))
  self.assertAlmostEqual(d['nearest_dedicated_pedestrian_node']['distance_m'],74.85508551392424)
  c=next(c for c in self.result['corrections'] if c['id']=='side-door-explicit-access-gap')
  self.assertEqual(c['target_geometry_class'],'road_explicit_foot');self.assertNotIn(471567486,c['source_osm_ids']['ways'])
 def test_candidate_false_way_incidence_rejected(self):
  c={'source_osm_ids':{'nodes':[1,2],'ways':[10]},'added_to_graph':False,'accepted':False}
  with self.assertRaises(ValueError):v2.validate_candidate_provenance(c,{1:None,2:None,3:None,4:None},{10:([3,4],{})})
if __name__=='__main__':unittest.main()
