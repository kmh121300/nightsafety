"""Read-only source audit and approximate facility proximity, not safety scoring."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, math, hashlib
import xml.etree.ElementTree as ET
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'project_readiness/data'
R = 6371000.0
LON0, LAT0 = 126.735, 37.3465
def xy(lon, lat):
    return (R*math.radians(lon-LON0)*math.cos(math.radians(LAT0)), R*math.radians(lat-LAT0))
def main():
    audit, groups, features = {}, {}, []
    for p in sorted((OUT/'source').rglob('*.csv')):
        rows = list(csv.DictReader(p.read_text(encoding='cp949').splitlines()))
        kind = 'cctv' if p.name.startswith('CCTV') else 'bell'
        valid, invalid = [], []
        for n, row in enumerate(rows, 2):
            try:
                lat, lon = float(row['WGS84위도']), float(row['WGS84경도'])
                assert math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180
                assert 33<=lat<=39 and 124<=lon<=132
                valid.append((lon,lat,row,n))
            except (ValueError,AssertionError): invalid.append(n)
        coords = Counter((lon,lat) for lon,lat,_,_ in valid)
        selected = valid if kind=='bell' else [x for x in valid if x[2]['설치목적구분']=='생활방범']
        outdoor = selected if kind=='cctv' else [x for x in selected if x[2]['설치장소유형']!='화장실']
        groups[kind+'_all'] = set((a,b) for a,b,_,_ in valid)
        groups[kind+'_eligible_unverified'] = set((a,b) for a,b,_,_ in outdoor)
        pilot = [x for x in valid if 126.719<=x[0]<=126.751 and 37.334<=x[1]<=37.359]
        audit[kind] = dict(source=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),encoding='cp949',rows=len(rows),valid_coordinates=len(valid),invalid_coordinate_csv_rows=invalid,unique_management_ids=len({r['관리번호'] for r in rows}),unique_coordinate_sites=len(coords),duplicate_coordinate_extra_rows=len(valid)-len(coords),coordinate_duplicate_groups=[{'coordinates':list(k),'count':v} for k,v in coords.items() if v>1],pilot_rows=len(pilot),pilot_unique_sites=len(set((a,b) for a,b,_,_ in pilot)),eligible_unique_sites=len(groups[kind+'_eligible_unverified']),eligible_pilot_sites=sum(126.719<=a<=126.751 and 37.334<=b<=37.359 for a,b in groups[kind+'_eligible_unverified']),fields={col:dict(Counter(r[col] for r in rows)) for col in ['설치목적구분','설치장소유형','경찰연계유무','최종점검결과구분','데이터기준일자','최종점검일자'] if col in rows[0]})
        if kind=='cctv': audit[kind]['reported_camera_units']=sum(int(r['카메라대수'] or 0) for r in rows)
        for lon,lat,row,n in pilot:
            props={'kind':kind,'csv_row':n,'source_file':p.name,'data_as_of':row['데이터기준일자'],'access_verified':False}
            for col in ['설치목적구분','설치장소유형','경찰연계유무','최종점검결과구분','소재지도로명주소','소재지지번주소']:
                if col in row: props[col]=row[col]
            features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':props})
    geo=json.loads((ROOT/'osm_poc_v2/routes-v2.geojson').read_text())
    route_edges=defaultdict(list)
    for f in geo['features']:
        if f['geometry']['type']=='LineString':route_edges[f['properties']['route']].append(f)
    trees={name:cKDTree([xy(*v) for v in coords]) for name,coords in groups.items() if coords}
    coverage={}
    for route, edges in route_edges.items():
        samples, weights=[],[]
        for f in edges:
            (a,b),(c,d)=f['geometry']['coordinates']
            distance=f['properties']['distance_m'];count=max(1,math.ceil(distance/5))
            for i in range(count):
                t=(i+.5)/count;samples.append(xy(a+(c-a)*t,b+(d-b)*t));weights.append(distance/count)
        total=sum(weights)
        coverage[route]={'distance_m':total,'samples':len(samples),'max_sample_interval_m':5,'metrics':{}}
        for name,tree in trees.items():
            dist,_=tree.query(samples)
            coverage[route]['metrics'][name]={str(radius):100*sum(w for w,v in zip(weights,dist) if v<=radius)/total for radius in [25,50,100]}
    osm=ET.parse(ROOT/'osm_poc_v2/raw.osm').getroot()
    node_xy={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in osm.findall('node')}
    police,lamps=[],[]
    for element in list(osm.findall('node'))+list(osm.findall('way')):
        tags={t.attrib['k']:t.attrib['v'] for t in element.findall('tag')}
        if tags.get('highway')=='street_lamp':lamps.append(element.attrib['id'])
        if tags.get('amenity')!='police':continue
        geom={'type':'Point','coordinates':node_xy[element.attrib['id']]} if element.tag=='node' else {'type':'Polygon','coordinates':[[node_xy[n.attrib['ref']] for n in element.findall('nd')]]}
        props={'kind':'police_osm_candidate','osm_type':element.tag,'osm_id':element.attrib['id'],'name':tags.get('name'),'official_status_verified':False,'entrance_verified':False}
        feature={'type':'Feature','geometry':geom,'properties':props}
        police.append(feature);features.append(feature)
    result={'data_audit':audit,'route_proximity':coverage,'shared_exact_cctv_bell_coordinates_city':len(groups['cctv_all']&groups['bell_all']),'shared_exact_cctv_bell_coordinates_pilot':sum(126.719<=a<=126.751 and 37.334<=b<=37.359 for a,b in groups['cctv_all']&groups['bell_all']),'police_osm_candidates':police,'osm_street_lamp_features':len(lamps),'method':'length-weighted <=5m midpoint samples, local equirectangular metric about pilot center; straight-line proximity only, no wall/road/visibility/access verification','radius_m':[25,50,100],'final_safety_score':None,'lighting_coordinates_verified':False,'police_official_coordinates_verified':False,'police_operational_status_verified':False,'graph_endpoint_completion_verified':False}
    (OUT/'facility-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (OUT/'pilot-facilities.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False))
    assert all(x['rows']==x['valid_coordinates']+len(x['invalid_coordinate_csv_rows']) for x in audit.values())
    assert all(0<=v<=100 for r in coverage.values() for m in r['metrics'].values() for v in m.values())
    assert all(m['25']<=m['50']<=m['100'] for r in coverage.values() for m in r['metrics'].values())
    print(json.dumps({'audit':audit,'proximity':coverage},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
