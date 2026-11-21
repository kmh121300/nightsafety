import unittest
import poc
class GraphTests(unittest.TestCase):
 def test_access_override(self):
  self.assertTrue(poc.accepted({'highway':'service','access':'private','foot':'yes'},'inferred'))
  self.assertFalse(poc.accepted({'highway':'footway','access':'yes','foot':'no'},'inferred'))
 def test_conservative_filters(self):
  for t in [{'highway':'motorway','foot':'yes'},{'highway':'service','access':'private'},{'highway':'footway','foot:conditional':'yes @ (Mo-Fr)'},{'highway':'service','sidewalk':'separate'},{'highway':'construction'},{'foot':'yes'}]:self.assertFalse(poc.accepted(t,'inferred'))
 def test_vehicle_oneway_and_foot_oneway(self):
  ns={1:((37,126),{}),2:((37,126.001),{})}
  g,_,_=poc.build(ns,{1:([1,2],{'highway':'footway','oneway':'yes'})},'explicit');self.assertTrue(g[2])
  g,_,_=poc.build(ns,{1:([1,2],{'highway':'footway','oneway:foot':'yes'})},'explicit');self.assertFalse(g[2])
 def test_no_geometric_joins(self):
  ns={1:((37,126),{}),2:((37,126.002),{}),3:((36.999,126.001),{}),4:((37.001,126.001),{})}
  g,_,_=poc.build(ns,{10:([1,2],{'highway':'footway'}),11:([3,4],{'highway':'footway','bridge':'yes','layer':'1'})},'explicit')
  self.assertIsNone(poc.shortest(g,ns,1,4)[0]);self.assertEqual(len(poc.components(g)[1]),2)
 def test_barrier(self):
  ns={1:((37,126),{}),2:((37,126.001),{'barrier':'gate'})}
  g,_,_=poc.build(ns,{1:([1,2],{'highway':'footway'})},'explicit');self.assertFalse(g)
  ns[2][1]['foot']='yes';g,_,_=poc.build(ns,{1:([1,2],{'highway':'footway'})},'explicit');self.assertTrue(g)
 def test_astar_matches_dijkstra(self):
  ns={1:((37,126),{}),2:((37,126.001),{}),3:((37.001,126.001),{}),4:((37.001,126.002),{})}
  g,_,_=poc.build(ns,{1:([1,2,4],{'highway':'footway'}),2:([1,3,4],{'highway':'footway'})},'explicit')
  self.assertAlmostEqual(poc.shortest(g,ns,1,4)[0],poc.shortest(g,ns,1,4,False)[0],places=8)
if __name__=='__main__':unittest.main()
