package kr.ac.tukorea.nightsafety

import android.app.Activity
import android.app.AlertDialog
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.ArrayAdapter
import kr.ac.tukorea.nightsafety.databinding.ViewSearchCardBinding
import kr.ac.tukorea.nightsafety.databinding.ViewResultPanelBinding
import kr.ac.tukorea.nightsafety.databinding.ViewToolbarBinding
import kr.ac.tukorea.nightsafety.databinding.DialogPlaceBinding
import kr.ac.tukorea.nightsafety.databinding.DialogFavoriteNameBinding
import kr.ac.tukorea.nightsafety.databinding.DialogFavoriteEditBinding
import kr.ac.tukorea.nightsafety.favorites.FavoriteRoute
import kr.ac.tukorea.nightsafety.favorites.FavoriteStore
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong
import java.util.Locale

/** Search and explicit user saves; no location history or provider response cache. */
class RouteWorkflow(
    private val activity: Activity,
    private val searchCard: ViewSearchCardBinding,
    private val resultPanel: ViewResultPanelBinding,
    private val toolbar: ViewToolbarBinding,
    private val getData: () -> PilotData?,
    private val getSelected: () -> Int,
    private val showData: (PilotData, Int) -> Unit,
    private val message: (String) -> Unit
) {
    private val network = Executors.newSingleThreadExecutor()
    private val database = Executors.newSingleThreadExecutor()
    private val handler = Handler(Looper.getMainLooper())
    private val api = RouteApi()
    private val store = FavoriteStore(activity)
    private val revision = AtomicLong()
    private var closed = false
    private var savedId = 0L
    private var shownRevision = -1L
    private var preferredProfile: String? = null
    private var origin = NamedPlace(GeoPoint(37.3418341, 126.7315593), "대학 옆문 실험점", "osm")
    private var destination = NamedPlace(GeoPoint(37.3517100, 126.7427421), "정왕역 1번출구", "osm")

    fun attach(state: Bundle?) {
        fun restore(prefix: String, fallback: NamedPlace): NamedPlace = if (state?.containsKey(prefix + "Lat") == true)
            NamedPlace(GeoPoint(state.getDouble(prefix + "Lat"), state.getDouble(prefix + "Lon")), state.getString(prefix + "Label") ?: fallback.label,
                state.getString(prefix + "Source") ?: "user_coordinate") else fallback
        origin = restore("origin", origin); destination = restore("destination", destination)
        searchCard.originInput.setOnClickListener { editPlace(true) }
        searchCard.destinationInput.setOnClickListener { editPlace(false) }
        searchCard.swapEndpoints.setOnClickListener {
            val previous = origin; origin = destination; destination = previous; changed()
        }
        searchCard.searchRoutes.setOnClickListener { search() }
        resultPanel.saveFavorite.setOnClickListener { saveFavorite() }
        toolbar.favoriteList.setOnClickListener { favorites() }
        labels()
        val snapshot = state?.getString("ownSnapshot")
        if (snapshot != null) runCatching {
            val restored = ServerBundleParser.parse(snapshot, getData()?.facilities ?: emptyList())
            showData(restored.copy(savedSnapshot = true), state.getInt("route", 0).coerceIn(0, (restored.routes.size - 1).coerceAtLeast(0)))
            message("복원된 이전 조회 결과 · 최신 검색으로 확인하세요")
        }
        else if (state != null) message("입력과 선택을 복원했습니다 · 저장/최신 상태 확인 전 다시 검색하세요")
    }

    private fun labels() {
        searchCard.originInput.apply { text = origin.label; contentDescription = "출발지 ${origin.label}" }
        searchCard.destinationInput.apply { text = destination.label; contentDescription = "도착지 ${destination.label}" }
    }

    private fun changed() {
        revision.incrementAndGet(); api.cancel(); savedId = 0; labels()
        message("입력이 바뀌었습니다 · 현재 선은 이전 결과입니다. 경로 검색을 눌러주세요")
    }

    fun useCurrentLocation(point: GeoPoint) {
        try { ServerBundleParser.checkedPoint(point.latitude, point.longitude) }
        catch (error: IllegalArgumentException) { message("현재 위치가 파일럿 밖입니다 · 기존 출발지 유지"); return }
        origin = NamedPlace(point, "현재 위치", "user_coordinate")
        changed()
    }

    fun chooseMapPoint(point: GeoPoint) {
        try { ServerBundleParser.checkedPoint(point.latitude, point.longitude) }
        catch (error: IllegalArgumentException) {
            AlertDialog.Builder(activity).setTitle("지원 지역 밖입니다")
                .setMessage("대학–정왕역 파일럿 지역 안의 위치를 선택해 주세요.")
                .setPositiveButton("확인", null).show()
            return
        }
        AlertDialog.Builder(activity).setTitle("지도에서 선택한 위치")
            .setItems(arrayOf("출발지로 설정", "도착지로 설정")) { _, index -> snapMapPoint(point, index == 0) }
            .setNegativeButton("취소", null).show()
    }

    private fun snapMapPoint(point: GeoPoint, isOrigin: Boolean) {
        val ticket = revision.incrementAndGet(); api.cancel()
        message("가까운 보행 지점을 찾는 중…")
        network.execute {
            if (ticket != revision.get()) return@execute
            val result = runCatching { api.snap(point) }
            post(ticket) {
                result.onSuccess { snap ->
                    val role = if (isOrigin) "출발지" else "도착지"
                    val gap = String.format(Locale.KOREA, "%.0f", snap.gapMeters)
                    val place = NamedPlace(snap.point, "지도 $role · ${gap}m 보정", "osm")
                    if (isOrigin) origin = place else destination = place
                    changed()
                    search()
                }.onFailure {
                    message("보행 지점 선택 실패 · 서버 연결과 파일럿 지역을 확인하세요")
                    AlertDialog.Builder(activity).setTitle("보행 지점을 찾지 못했습니다")
                        .setMessage("서버 연결과 파일럿 지역을 확인한 뒤 다시 선택해 주세요. 기존 출발·도착은 유지됩니다.")
                        .setPositiveButton("확인", null).show()
                }
            }
        }
    }

    private fun editPlace(isOrigin: Boolean) {
        val selected = if (isOrigin) origin else destination
        val binding = DialogPlaceBinding.inflate(activity.layoutInflater)
        val query = binding.placeQuery
        val label = binding.placeLabel.apply { setText(selected.label) }
        val latitude = binding.placeLatitude.apply { setText(selected.point.latitude.toString()) }
        val longitude = binding.placeLongitude.apply { setText(selected.point.longitude.toString()) }
        val lookup = binding.placeLookup
        val dialog = AlertDialog.Builder(activity).setTitle(if (isOrigin) "출발지 설정" else "도착지 설정")
            .setView(binding.root).setPositiveButton("좌표 적용", null).setNegativeButton("닫기", null).create()
        lookup.setOnClickListener {
            val search = query.text.toString().trim()
            if (search.isBlank()) { query.error = "검색어를 입력하세요"; return@setOnClickListener }
            val ticket = revision.incrementAndGet(); api.cancel()
            message("장소를 찾는 중…")
            network.execute {
                val result = runCatching { api.places(search) }
                post(ticket) {
                    result.onSuccess { places ->
                        if (places.isEmpty()) {
                            query.error = "검색 결과 없음 · 직접 좌표를 입력하세요"
                            message("검색 결과 없음 · 직접 좌표를 입력하세요")
                            return@onSuccess
                        }
                        AlertDialog.Builder(activity).setTitle("장소 · 출입구 미검증")
                            .setItems(places.map { it.label }.toTypedArray()) { _, index ->
                                val place = places[index]
                                if (isOrigin) origin = place else destination = place
                                changed(); dialog.dismiss()
                            }.setNegativeButton("닫기", null).show()
                    }.onFailure { message("장소 검색 실패 · 로컬 서버 실행과 연결을 확인하세요") }
                }
            }
        }
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                runCatching {
                    val point = ServerBundleParser.checkedPoint(latitude.text.toString().toDouble(), longitude.text.toString().toDouble())
                    val name = label.text.toString().trim()
                    require(name.length in 1..50) { "이름은 1~50자로 입력하세요" }
                    NamedPlace(point, name)
                }.onSuccess { if (isOrigin) origin = it else destination = it; changed(); dialog.dismiss() }
                    .onFailure { latitude.error = it.message ?: "좌표를 확인하세요" }
            }
        }
        dialog.show()
    }

    fun search(preferred: String? = null) {
        val start = origin; val end = destination
        val ticket = revision.incrementAndGet(); api.cancel()
        message("서버에서 경로·시설 지표를 계산하는 중…")
        network.execute {
            if (ticket != revision.get()) return@execute
            val result = runCatching { ServerBundleParser.parse(api.compare(start, end), getData()?.facilities ?: emptyList()) }
            post(ticket) {
                result.onSuccess { parsed ->
                    val index = parsed.routes.indexOfFirst { preferred in it.profiles }.coerceAtLeast(0)
                    shownRevision = ticket
                    preferredProfile = preferred
                    showData(parsed.copy(origin = start.point, destination = end.point), index)
                    message(if (parsed.routes.isEmpty()) "연결된 후보가 없습니다 · 출발/도착 보행 지점을 바꿔주세요"
                        else "서버 검색 완료 · 공공시설 기반 안전지표")
                }.onFailure { message("경로 검색 실패: ${it.message ?: "로컬 서버 연결을 확인하세요"} · 이전 결과 유지") }
            }
        }
    }

    private fun saveFavorite() {
        val data = getData() ?: return
        if (data.routes.isEmpty()) { message("저장할 경로가 없습니다"); return }
        if (shownRevision != revision.get() || data.savedSnapshot) { message("현재 입력으로 최신 경로를 검색한 뒤 저장하세요"); return }
        val capturedRevision = revision.get()
        val capturedOrigin = origin
        val capturedDestination = destination
        val capturedId = savedId
        val capturedRoute = data.routes[getSelected().coerceIn(data.routes.indices)]
        val capturedProfile = preferredProfile?.takeIf { it in capturedRoute.profiles } ?: capturedRoute.profiles.firstOrNull() ?: "fast"
        val binding = DialogFavoriteNameBinding.inflate(activity.layoutInflater)
        val title = binding.root.apply { setText("${origin.label} → ${destination.label}") }
        AlertDialog.Builder(activity).setTitle("즐겨찾기 저장").setView(binding.root)
            .setPositiveButton("저장") { _, _ ->
                if (revision.get() != capturedRevision) { message("입력이 변경됐습니다 · 다시 검색 후 저장하세요"); return@setPositiveButton }
                val record = FavoriteRoute().apply {
                    id = capturedId; this.title = title.text.toString()
                    originLatitude = capturedOrigin.point.latitude; originLongitude = capturedOrigin.point.longitude
                    destinationLatitude = capturedDestination.point.latitude; destinationLongitude = capturedDestination.point.longitude
                    originLabel = capturedOrigin.label; destinationLabel = capturedDestination.label
                    originSource = capturedOrigin.source; destinationSource = capturedDestination.source
                    preferredProfile = capturedProfile
                    snapshotJson = data.snapshotJson
                }
                db({ store.save(record) }) { id ->
                    if (revision.get() == capturedRevision) savedId = id
                    message("즐겨찾기를 기기에 저장했습니다")
                }
            }.setNegativeButton("취소", null).show()
    }

    private fun favorites() {
        db({ store.list() }) { records ->
            if (records.isEmpty()) { message("저장된 즐겨찾기가 없습니다"); return@db }
            AlertDialog.Builder(activity).setTitle("즐겨찾기")
                .setItems(records.map { it.title }.toTypedArray()) { _, index -> favoriteActions(records[index]) }
                .setNegativeButton("닫기", null).show()
        }
    }

    private fun favoriteActions(record: FavoriteRoute) {
        AlertDialog.Builder(activity).setTitle(record.title)
            .setItems(arrayOf("저장 결과 보기 (오프라인)", "최신 자료로 재조회", "이름·선호유형 수정", "삭제")) { _, action ->
                when (action) {
                    0 -> openFavorite(record, false)
                    1 -> openFavorite(record, true)
                    2 -> editFavorite(record)
                    3 -> db({ store.delete(record.id) }) {
                        if (savedId == record.id) savedId = 0
                        message("즐겨찾기를 삭제했습니다")
                    }
                }
            }.setNegativeButton("닫기", null).show()
    }

    private fun openFavorite(record: FavoriteRoute, requery: Boolean) {
        origin = NamedPlace(GeoPoint(record.originLatitude, record.originLongitude), record.originLabel, record.originSource)
        destination = NamedPlace(GeoPoint(record.destinationLatitude, record.destinationLongitude), record.destinationLabel, record.destinationSource)
        changed(); savedId = record.id; preferredProfile = record.preferredProfile
        if (requery) { search(record.preferredProfile); return }
        if (record.snapshotJson == null) { message("저장된 위치만 복원했습니다 · 경로 검색이 필요합니다"); return }
        runCatching { ServerBundleParser.parse(record.snapshotJson, getData()?.facilities ?: emptyList()) }
            .onSuccess { parsed ->
                showData(parsed.copy(savedSnapshot = true), parsed.routes.indexOfFirst { record.preferredProfile in it.profiles }.coerceAtLeast(0))
                message("저장된 과거 결과 · 선호유형 변경/최신 버전은 재조회로 확인하세요")
            }.onFailure { message("저장 결과를 읽지 못했습니다 · 위치는 복원됐으니 재조회하세요") }
    }

    private fun editFavorite(record: FavoriteRoute) {
        val binding = DialogFavoriteEditBinding.inflate(activity.layoutInflater)
        val name = binding.favoriteName.apply { setText(record.title) }
        val profiles = listOf("fast", "safe", "balanced", "pedestrian")
        val profile = binding.favoriteProfile.apply {
            adapter = ArrayAdapter(activity, android.R.layout.simple_spinner_dropdown_item, arrayOf("빠른 경로", "안전 우선 경로", "균형 경로", "보행선 우선"))
            setSelection(profiles.indexOf(record.preferredProfile).coerceAtLeast(0))
        }
        AlertDialog.Builder(activity).setTitle("즐겨찾기 수정").setView(binding.root)
            .setPositiveButton("수정") { _, _ -> db({ store.rename(record.id, name.text.toString(), profiles[profile.selectedItemPosition]) }) {
                message("이름·유형 수정 완료 · 저장 선형은 최신 재조회 전까지 과거 결과입니다")
            } }.setNegativeButton("취소", null).show()
    }

    private fun <T> db(work: () -> T, completed: (T) -> Unit) {
        database.execute {
            val result = runCatching(work)
            handler.post { if (!closed && !activity.isDestroyed) result.onSuccess(completed).onFailure { message(it.message ?: "저장소 오류") } }
        }
    }

    private fun post(ticket: Long, action: () -> Unit) = handler.post {
        if (!closed && !activity.isDestroyed && revision.get() == ticket) action()
    }
    fun saveState(state: Bundle) {
        for ((prefix, place) in listOf("origin" to origin, "destination" to destination)) {
            state.putDouble(prefix + "Lat", place.point.latitude); state.putDouble(prefix + "Lon", place.point.longitude)
            state.putString(prefix + "Label", place.label); state.putString(prefix + "Source", place.source)
        }
        // Keep large route payloads out of Binder state; Room holds explicit offline snapshots.
        getData()?.snapshotJson?.takeIf { it.length < 80_000 }?.let { state.putString("ownSnapshot", it) }
    }

    fun close() {
        closed = true; revision.incrementAndGet(); api.cancel(); network.shutdownNow()
        handler.removeCallbacksAndMessages(null)
        database.execute { store.close() }; database.shutdown()
    }
}
