import pathlib,json,xml.etree.ElementTree as ET,math,html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator,FormatStrFormatter
import poc,poc_v2
P=pathlib.Path(__file__).resolve().parent;r=json.loads((P/'result-v2.json').read_text());raw=ET.parse(P/'raw.osm').getroot()
if r['policy']['multipliers'] != {'dedicated_pedestrian':1.,'road_explicit_foot':2.,'road_inferred_foot':4.}:
 raise ValueError('This before/after report documents default 2/4 policy. Run python poc_v2.py first; custom policy results remain available in JSON/GeoJSON.')
ns={int(n.attrib['id']):(float(n.attrib['lon']),float(n.attrib['lat'])) for n in raw.findall('node')};ws={int(w.attrib['id']):([int(n.attrib['ref']) for n in w.findall('nd')],poc.tags(w)) for w in raw.findall('way')}
colors={'dedicated_pedestrian':'#15966b','road_explicit_foot':'#2563eb','road_inferred_foot':'#db6233'}
fig,axes=plt.subplots(1,3,figsize=(18,9),gridspec_kw={'width_ratios':[1.4,1.4,1]})
for a in axes:
 for ids,t in ws.values():
  if 'highway' in t:
   co=[ns[n] for n in ids if n in ns]
   if len(co)>1:a.plot(*zip(*co),color='#d3d9df',lw=.45,zorder=0)
 ids,t=ws[234844934];co=[ns[n] for n in ids];a.fill(*zip(*co),color='#dcf1e3',alpha=.7,zorder=1)
 a.set_aspect(1/math.cos(math.radians(37.345)));a.grid(alpha=.15);a.ticklabel_format(useOffset=False);a.set_xlabel('Longitude');a.set_ylabel('Latitude');a.xaxis.set_major_locator(MaxNLocator(4));a.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
for a,name in [(axes[0],'distance_only'),(axes[1],'pedestrian_preferred'),(axes[2],'pedestrian_preferred')]:
 rt=r['routes'][name]
 for e in rt['segments']:a.plot(*zip(ns[e['from']],ns[e['to']]),color=colors[e['class']],lw=3,zorder=3)
 snap=r['destination']['snap_node'];a.plot(*zip(ns[snap],ns[poc.DEST]),color='#be123c',linestyle='--',lw=2,zorder=5)
 a.scatter(*ns[poc.DEST],color='#be123c',s=35,zorder=6);a.scatter(*ns[snap],facecolors='white',edgecolors='#be123c',s=20,zorder=6)
 if a!=axes[2]:
  a.scatter(*ns[poc.START],color='#111827',s=35,zorder=5);a.annotate('Mapped exterior endpoint',ns[poc.START],xytext=(5,-18),textcoords='offset points',fontsize=8)
  a.annotate('Exit 1: unresolved',ns[poc.DEST],xytext=(-5,10),textcoords='offset points',ha='right',fontsize=8)
  a.set_xlim(126.730,126.7455);a.set_ylim(37.3385,37.353)
axes[0].set_title('Before: distance only\n1,572.40 m | dedicated pedestrian 0.17%',fontsize=12)
axes[1].set_title('After: geometry preference (2 / 4)\n1,932.56 m | dedicated pedestrian 76.40%',fontsize=12)
axes[2].set_xlim(126.7419,126.7434);axes[2].set_ylim(37.3509,37.3520);axes[2].set_title('Endpoint remains unresolved\n12.56 m gap is NOT an edge',fontsize=12)
axes[2].xaxis.set_major_locator(MaxNLocator(3));axes[2].xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
axes[2].annotate('Exit: 3403277121',ns[poc.DEST],xytext=(-105,18),textcoords='offset points',fontsize=9)
axes[2].annotate('Graph: 4665188383',ns[snap],xytext=(-105,-25),textcoords='offset points',fontsize=9)
fig.suptitle('OSM PoC v2: more mapped pedestrian geometry, exact route still incomplete',fontsize=17)
handles=[Line2D([0],[0],color=c,lw=3,label=l) for c,l in [('#15966b','Dedicated pedestrian geometry'),('#2563eb','Road geometry with foot=yes'),('#db6233','Road geometry: foot permission inferred'),('#be123c','Unverified exit gap; never inserted')]]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.04),ncol=2,fontsize=10)
fig.text(.01,.012,'© OpenStreetMap contributors • ODbL • Same raw snapshot, zero topology edits • Preference weights are not a facility safety score',fontsize=10)
fig.subplots_adjust(bottom=.19,top=.87,wspace=.25);fig.savefig(P/'route-v2.png',dpi=160);fig.savefig(P/'route-v2.svg');plt.close(fig)
svg=(P/'route-v2.svg').read_text();svg=svg[svg.index('<svg'):]
base=r['routes']['distance_only'];pref=r['routes']['pedestrian_preferred'];moderate=r['routes']['moderate_pedestrian_preferred'];broad=base['distance_m']-base['geometry_distance_m']['dedicated_pedestrian'];proad=pref['distance_m']-pref['geometry_distance_m']['dedicated_pedestrian']
labels={'distance_only':'기존 거리최소','moderate_pedestrian_preferred':'보행선 우선 1.5/3','pedestrian_preferred':'보행선 우선 2/4','primary_secondary_excluded':'기존 primary/secondary 제외'}
rows='\n'.join(f"| {labels[n]} | {a['distance_m']:.2f}m | {a['geometry_share_percent']['dedicated_pedestrian']:.2f}% | {a['distance_m']-a['geometry_distance_m']['dedicated_pedestrian']:.2f}m | {a['shared_percent_of_distance_only']:.2f}% |" for n,a in r['routes'].items())
sens='\n'.join(f"| {x['multipliers']['road_explicit_foot']:g} / {x['multipliers']['road_inferred_foot']:g} | {x['distance_m']:.2f}m | {x['pedestrian_share_percent']:.2f}% | {x['policy_cost']:.2f} |" for x in r['sensitivity'])
correction_rows=[]
for c in r['corrections']:
 coords=' → '.join(f'{x[0]:.7f},{x[1]:.7f}' for x in [c['coordinates_lat_lon'][0],c['coordinates_lat_lon'][-1]])
 correction_rows.append(f"| {c['id']} | {c.get('gap_m',c.get('distance_m',0)):.2f}m | {coords} | {json.dumps(c['source_osm_ids'],ensure_ascii=False)} |")
cr='\n'.join(correction_rows)
report=f'''# OSM 보행 그래프 PoC v2 — 보행선 우선으로 실제 개선

**원본 topology를 유지하면서 전용 보행선 이용률을 0.17% → 76.40%로 높였다.** 경로는 1,572.40m → 1,932.56m(+360.16m, +22.90%)이고 도로 선형 의존 길이는 {broad:.2f}m → {proad:.2f}m(70.94% 감소)이다. 다만 정왕역 1번출구 연결은 여전히 미검증이므로 기본 결과는 `route_incomplete`, `exact_route=null`이다. 안전 시설 점수·현장 보행 검증·OSM 외부 편집은 수행하지 않았다.

## 무엇을 보완했나

1. 단순 거리최소를 **보행선 우선 / 데이터 확실성 페널티**로 확장했다. 원본 전용 footway/pedestrian/path/steps, foot=yes 도로, foot 미지정 도로의 geometry를 구분한다. 주 정책은 거리×1/2/4이며 값은 실험용 선택 가중치로 경험적으로 보정된 확률/안전 점수가 아니다. 명시 보행 허용이 있어도 도로 선형은 별도 인도 위치를 나타내지 않는다.
2. 거리와 정책 비용을 별도 출력한다. 동일 정책 비용이면 실제 거리가 짧은 경로를 선택한다. 가중치는 `--foot-road-multiplier`, `--inferred-road-multiplier`로 바꿀 수 있고 모두1 이상인 유한값만 허용한다.
3. 정확한 출구 노드까지 완결되었는지 검사하고, 스냅 경로는 `review_candidate_route_incomplete`로만 반환한다. node/segment 스냅 후보를 분리했으며 segment projection도 새로운 연결 근거로 쓰지 않는다.
4. 원본 node/way ID와 근거를 포함한 수리 검토 후보 JSON·GeoJSON을 만들었다. 자동 근접 연결·도로 offset 보도 생성·미검증 overlay 주입은 하지 않는다. topology 수정0개, connector simulation기본비활성.

## 경로 비교

모든 거리는 옆문 도보 바깥 endpoint node9799703999 → 그래프 node4665188383까지이다. 정왕역 실제 출구 node3403277121까지의12.56m 미검증 간극은 거리에 더하지 않았다.

| 후보 정책 | 실제 거리 | 전용 보행선 비율 | 도로 geometry 길이 | 기존 최단과 공통 방향 edge 비율 |
|---|---:|---:|---:|---:|
{rows}

2/4 후보의 구성은 전용 보행선1,476.48m, foot=yes 도로162.66m, 미지정 도로293.42m이다. 기존 최단과 공통 edge241.93m(15.39%)라서 상당 부분 다른 선형을 이용한다. 비용은2,975.49 정책 단위이며 이 값을2,975.49m 보행거리로 표시해서는 안 된다.

실제 활용한 선형에는 sidewalk way1495768614/1495767511/1495767507, lit=yes footway472321927, marked crossing472321928, pedestrian **중심상가3길** way471592948, bridge footway471592949가 있다. bridge의 공유 끝점에서 일반 footway로 이동하는 원본 연결도 유지한다. 경로 crossing 노드는11개이나 개수만으로 안전 우열을 판단하지 않는다. lit=yes도 현장 조도나 현재 운행 상태를 측정한 값이 아니다.

내부 보조 출발 node9799703963(37.3412571,126.7324818)의2/4 경로는1,868.11m, 전용 보행선76.38%다. 대학 service 선형을 이용한 후 외부 footway/bridge/steps 경로로 나가며 way472321926에는 step_count=88, ramp:wheelchair=yes가 있다. 접근 가능성·경사·휠체어 적합성·교문 운영을 확인하지 않았고 도착은 똑같이 미완결이다. 이것은 지정 교문 확정 결과가 아니다.

## 원인 진단과 근거가 없는 수리의 보류

명시 보행 허용 그래프는71개 약연결 성분이다. 출발 근처 성분305노드, 역 근처 성분15노드가 서로 분리되어 있다. 기존 최단 알고리즘은 road geometry shortcut을 선택하면서 이미 매핑된 별도 sidewalk·상가 보행선을 대부분 쓰지 않았다. v2는 연결을 새로 만들어 단절을 숨기지 않고 기존 연결에서 선형 선호를 개선했다.

출발 근처 가장 가까운 explicit 노드4130186271까지11.30m지만 이 노드는 **footway가 아닌 foot=yes tertiary 도로** way493192211과 service411314663의 공유 노드다. 실제 가장 가까운 전용 보행선 노드는13702949093, sidewalk way1495769487, 거리74.86m다. 두 항목을 혼동하지 않도록 sourceway incidence 감사와 회귀 검증을 추가했다.

정왕역 1번출구는 어떤 highway way에도 포함되지 않은 독립 node다. 가장 가까운 보행 segment way472303067로의 투영 fraction=0이므로 기존 snap node4665188383과 같은 점이다. node→segment 스냅을 바꿔도12.56m 간극은 해소되지 않는다.

pedestrian area2개(way471765493,1052014080)를 조사했다. 첫째는 기존 보행선과 공유 node가 있으나 출구를 포함하지 않고, 둘째도 출구를 포함하지 않으며 기존 선형 그래프와 공유 node가 없다. 따라서 pedestrian area를 근거로 출구 connector를 추가할 수 없었다.

## 현장 확인할 수리 검토 후보

아래 선형들은 `unverified_review_candidate`, accepted=false, added_to_graph=false로만 저장한다. component 사이 직선과12.56m 출구 간극은 실제로 걸을 수 있는 길을 관측했다는 뜻이 아니다. 원본 도로 run은 별도 보도 위치와 횡단 연속성 확인 대상으로 남긴다.

| 후보 ID | 간극 또는 road run 길이 | 위도,경도 시작 → 끝 | 원본 node/way 근거 |
|---|---:|---|---|
{cr}

우선 조사할 도로 run은 옆문 외부 service76.53m, 마유로 foot=yes tertiary162.66m, 군서마을로/마유로 residential216.90m이다. 두 explicit 성분의 최단 node 쌍 간극101.06m도 단순 기하학 후보일 뿐 자동 연결하지 않는다. source ID가 실제 후보 node에 incident한지 검증하며, 미지정도로를 포함한 경로는 보행 적법성·보도 연속성 확인이 남아 있다.

캠퍼스 polygon way234844934를 그대로 쓰며, 이전 좌표37.34278,126.72861은 polygon 밖이라는 v1 진단을 유지한다. 옆문 실험점은 이름 `기숙사-옆문 도보`를 갖는 원본 way1067311761의 바깥쪽 endpoint를 쓴다. 명시 entrance/barrier=gate가 아니므로 실제 사용할 교문·통행시간은 아직 확정하지 않는다.

## 민감도와 알고리즘 검증

| foot 허용 도로 / 미지정도로 배수 | 실제 거리 | 전용 보행선 비율 | 정책 비용 |
|---|---:|---:|---:|
{sens}

배수1.5/3에서1.813km·65.54%,2/4에서1.933km·76.40%,4/12와10/30은2/4와 같은 선형을 선택했다. 가중치 변화가 실제 경로에 영향을 주므로 UI나 API에서도 사용 정책을 기록해야 한다. safety 추천은 제공하지 않는다.

A* heuristic은 구면 직선거리이며 모든 edge 비용이 실제 구면거리 이상이므로 admissible하다. 목표 도달 후에도 동일한 비용 lower-bound를 처리하여 정책 비용 동률에서 짧은 거리를 정한다. 모든 정책·민감도에서 자체 A*와 Dijkstra의 **정책 비용**이 일치했고 거리 동률 선택도 일치했다. 부모 작업의 별도 SciPy sparse csgraph Dijkstra도2/4 정책 비용2,975.4893480921746, 실제 거리1,932.5627727980034m를 독립 재현했다.

현재 검증16개가 통과한다: access 우선, 제한, vehicle/foot 방향, barrier, 교차 geometry의 비연결, 비용 최적성, 거리 동률, 부적절 가중치 거절, endpoint 미완결, 원본 보존, 불법 shortcut·가짜 provenance 거절, 후보 검토 상태, 도로/footway 구분, 스냅의 비연결 등이 포함된다. 모든 반환 edge는 원본 way의 연속 node이며 원본 SHA256도 v1과 같다.

## 남아 있는 판단

보행선 우선 후보는 geometry 의존도를 개선했지만 route_complete가 되는 조건은 아직 충족하지 않는다. 실제 교문·출구 connector·road run의 인도 위치/횡단 연결을 현장 또는 공식 시설 도면으로 확인한 후 증거와 상태를 기록하고 그래프를 갱신해야 한다. 이 후에도 OSM tag가 물리적 현황 전체를 보증하지 않으므로 보행 가능성과 시설 안전 점수는 별도 확인한다. bbox 밖 우회, 조건부 통행·운영시간, 휠체어 접근, 조도·사고·CCTV·가로등 위치는 현재 검증 범위 밖이다. 도로 선형을 시설30m 거리 계산에 사용하면 위치 오차가 커질 수 있다.

TMAP 비교는 키/보행 응답이 없어 실행하지 않았고 Supabase/app 배포는 진행하지 않았다. 이번 변경은 로컬 연구 PoC의 실제 라우팅 정책·반환 상태·검토 자료 개선이다.

## 재현

```sh
python poc_v2.py
python -m unittest discover -s . -p 'test*.py' -v
python make_report_v2.py
# 선택 정책 예시
python poc_v2.py --foot-road-multiplier 1.5 --inferred-road-multiplier 3
```

선택 옵션 실행 시 result-v2.json과 routes-v2.geojson가 바뀐다. 이 비교 보고서·그림 생성기는 기본2/4 결과 전용이며, custom 실험 후 다시 생성하려면 먼저 `python poc_v2.py`로 기본 결과를 복원한다. custom 선택값으로 기본 수치 보고서를 생성하는 것은 거절한다. 공유 원본과 v1 코드(poc.py)는 보존했다. 설치 의존성은 표준 Python 및 그림 생성의 matplotlib이다.

공식 원본 URL: {r['source_url']}
수집 UTC: {r['acquisition']['retrieved_utc']}; 7,919,876bytes; SHA256 `{r['raw_sha256']}`.
© OpenStreetMap contributors / ODbL: https://www.openstreetmap.org/copyright
태그·모델링 근거: https://wiki.openstreetmap.org/wiki/Key:foot · https://wiki.openstreetmap.org/wiki/Key:access · https://wiki.openstreetmap.org/wiki/Key:oneway:foot · https://wiki.openstreetmap.org/wiki/Guidelines_for_pedestrian_navigation
'''
(P/'report-v2-ko.md').write_text(report)
htrows=''.join(f"<tr><td>{html.escape(labels[n])}</td><td>{a['distance_m']:.2f}m</td><td>{a['geometry_share_percent']['dedicated_pedestrian']:.2f}%</td><td>{a['distance_m']-a['geometry_distance_m']['dedicated_pedestrian']:.2f}m</td><td>route_incomplete</td></tr>" for n,a in r['routes'].items())
(P/'route-v2.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>OSM 보행 PoC v2</title><style>body{font-family:system-ui;margin:24px;max-width:1900px;line-height:1.6}svg{width:100%;height:auto}table{border-collapse:collapse}td,th{padding:10px;border:1px solid #bbb}code{background:#eee;padding:3px}</style><h1>보행선을 더 활용하도록 보완한 OSM PoC v2</h1><p>기존0.17% → 보행선 우선76.40%, 도로 선형1,569.66m → 456.08m. 실제 거리는1,572.40m → 1,932.56m. 기본 결과는 <code>route_incomplete</code>이며 정왕역 출구의12.56m 간극을 연결하지 않았습니다. 보행 적법성·현장 안전 검증은 남아 있습니다.</p>'+svg+'<table><thead><tr><th>정책</th><th>실제 거리</th><th>전용 보행선 비율</th><th>도로 geometry</th><th>상태</th></tr></thead><tbody>'+htrows+'</tbody></table><p>가중치는 전용 보행선1 / foot 허용 도로2 / 미지정 도로4의 실험용 선호 정책입니다. 범죄·조도·시설 안전 점수가 아닙니다. 모든 경로는 원본 연속 OSM node만 연결하며 수리 검토 후보는 실제 그래프에 추가하지 않았습니다.</p><p>© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors / ODbL</a>. 공식 원본 동일 snapshot, topology 변경0개.</p></html>')
print('Generated report-v2-ko.md, route-v2.png, route-v2.svg, route-v2.html')
