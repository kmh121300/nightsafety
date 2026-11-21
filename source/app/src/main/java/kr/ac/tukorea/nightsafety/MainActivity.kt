package kr.ac.tukorea.nightsafety

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.pm.PackageManager
import android.content.res.Configuration
import android.graphics.Rect
import android.location.LocationManager
import android.os.Build
import android.os.Bundle
import android.os.CancellationSignal
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.View
import android.view.MotionEvent
import android.view.ViewConfiguration
import android.view.ViewGroup
import android.widget.FrameLayout
import android.window.OnBackInvokedCallback
import android.window.OnBackInvokedDispatcher
import androidx.core.widget.NestedScrollView
import com.google.android.material.bottomsheet.BottomSheetBehavior
import android.widget.CheckBox
import android.widget.ArrayAdapter
import android.widget.AdapterView
import android.widget.Toast
import kr.ac.tukorea.nightsafety.databinding.ActivityMainBinding
import kr.ac.tukorea.nightsafety.databinding.ViewToolbarBinding
import kr.ac.tukorea.nightsafety.databinding.ViewSearchCardBinding
import kr.ac.tukorea.nightsafety.databinding.ViewMapPanelBinding
import kr.ac.tukorea.nightsafety.databinding.ViewResultPanelBinding
import kr.ac.tukorea.nightsafety.databinding.ViewRouteOptionBinding
import java.util.Locale
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val loader = Executors.newSingleThreadExecutor()
    private val handler = Handler(Looper.getMainLooper())
    private var data: PilotData? = null
    private var preview: PilotPreviewView? = null
    private var map: TmapPilotMap? = null
    private var selected = 0
    private var showLocal = BuildConfig.TMAP_APP_KEY.isBlank()
    private var location: GeoPoint? = null
    private var locationRequest: CancellationSignal? = null
    private var resumed = false
    private var showWeak = false
    private var bindingRoutes = false
    private var mapFullscreen = false
    private var topCardMinimized = false
    private var mapEndMargin = 0
    private var fullscreenBack: OnBackInvokedCallback? = null
    private lateinit var workflow: RouteWorkflow
    private var workflowAttached = false
    private var restoreState: Bundle? = null
    private lateinit var binding: ActivityMainBinding
    private lateinit var toolbar: ViewToolbarBinding
    private lateinit var searchCard: ViewSearchCardBinding
    private lateinit var mapPanel: ViewMapPanelBinding
    private lateinit var resultPanel: ViewResultPanelBinding
    private lateinit var controls: NestedScrollView
    private var sheet: BottomSheetBehavior<NestedScrollView>? = null
    private var navigationInset = 0
    private var statusInset = 0
    private lateinit var filters: List<CheckBox>
    private val status get() = toolbar.mapStatus
    private val container get() = mapPanel.mapContainer
    private val kinds = listOf("cctv", "bell", "police_osm_candidate", "lamp")

    override fun attachBaseContext(newBase: Context) {
        // shortcut: MVP fixes app text size; revisit system text scaling before public release.
        super.attachBaseContext(newBase.createConfigurationContext(Configuration().apply { fontScale = 1f }))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        val pane = binding.twoPane
        toolbar = binding.toolbar ?: requireNotNull(pane).toolbar
        searchCard = binding.searchCard ?: requireNotNull(pane).searchCard
        mapPanel = binding.mapPanel ?: requireNotNull(pane).mapPanel
        resultPanel = binding.resultPanel ?: requireNotNull(pane).resultPanel
        controls = binding.controlsScroll ?: requireNotNull(pane).controlsScroll
        sheet = if (binding.topContainer != null) BottomSheetBehavior.from(controls) else null
        configureRouteSheet()
        resultPanel.routeSummary.addOnLayoutChangeListener { _, _, _, _, _, _, _, _, _ -> updateSheetLayout() }
        binding.root.addOnLayoutChangeListener { _, _, _, _, _, _, _, _, _ -> updateSheetLayout() }
        mapEndMargin = (mapPanel.root.layoutParams as ViewGroup.MarginLayoutParams).marginEnd
        filters = listOf(resultPanel.cctvFilter, resultPanel.bellFilter, resultPanel.policeFilter, resultPanel.lampFilter)
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
        binding.root.setOnApplyWindowInsetsListener { _, insets ->
            navigationInset = insets.systemWindowInsetBottom
            statusInset = insets.systemWindowInsetTop
            val top = binding.topContainer
            if (top != null) {
                top.layoutParams = (top.layoutParams as ViewGroup.MarginLayoutParams).apply {
                    topMargin = insets.systemWindowInsetTop + dp(12)
                    marginStart = insets.systemWindowInsetLeft + dp(12)
                    marginEnd = insets.systemWindowInsetRight + dp(12)
                }
                binding.expandTopCard?.let { button ->
                    button.layoutParams = (button.layoutParams as ViewGroup.MarginLayoutParams).apply {
                        topMargin = statusInset + dp(12)
                        marginEnd = insets.systemWindowInsetRight + dp(12)
                    }
                }
                controls.setPadding(insets.systemWindowInsetLeft, 0, insets.systemWindowInsetRight, navigationInset)
                binding.navigationScrim?.let { scrim ->
                    scrim.layoutParams = scrim.layoutParams.apply { height = navigationInset }
                }
                binding.sheetRestoreArea?.let { edge ->
                    edge.layoutParams = (edge.layoutParams as ViewGroup.MarginLayoutParams).apply {
                        bottomMargin = navigationInset
                    }
                }
            } else {
                binding.root.setPadding(insets.systemWindowInsetLeft, insets.systemWindowInsetTop,
                    insets.systemWindowInsetRight, navigationInset)
            }
            updateSheetLayout()
            insets
        }
        selected = savedInstanceState?.getInt("route", 0) ?: 0
        restoreState = savedInstanceState
        showLocal = savedInstanceState?.getBoolean("local", showLocal) ?: showLocal
        topCardMinimized = savedInstanceState?.getBoolean("top_card_minimized", false) ?: false
        toolbar.minimizeTopCard.visibility = if (binding.topContainer != null) View.VISIBLE else View.GONE
        toolbar.minimizeTopCard.setOnClickListener {
            topCardMinimized = true
            updateTopCardVisibility()
        }
        binding.expandTopCard?.setOnClickListener {
            topCardMinimized = false
            updateTopCardVisibility()
        }
        filters.forEachIndexed { index, filter ->
            filter.apply {
                isChecked = savedInstanceState?.getBoolean(kinds[index], true) ?: true
                setOnCheckedChangeListener { _, _ -> refresh() }
            }
        }
        resultPanel.routeSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                if (!bindingRoutes) { selected = position; refresh() }
            }
            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }
        mapPanel.preview.setOnClickListener {
            showLocal = if (BuildConfig.TMAP_APP_KEY.isBlank()) true else !showLocal
            displayMap()
        }
        mapPanel.resetMap.setOnClickListener { setMapFullscreen(!mapFullscreen) }
        setMapFullscreen(savedInstanceState?.getBoolean("map_fullscreen", false) ?: false)
        mapPanel.location.setOnClickListener { requestLocation() }
        resultPanel.facilityList.setOnClickListener { showFacilities() }
        resultPanel.weakSegments.setOnClickListener { showWeakSegments() }
        resultPanel.dataInfo.setOnClickListener { showDataInfo() }
        workflow = RouteWorkflow(this, searchCard, resultPanel, toolbar, { data }, { selected }, ::applyServerData, { status.text = it })
        loadData()
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    private fun configureRouteSheet() {
        sheet?.addBottomSheetCallback(object : BottomSheetBehavior.BottomSheetCallback() {
            override fun onStateChanged(bottomSheet: View, newState: Int) {
                if (newState == BottomSheetBehavior.STATE_EXPANDED || newState == BottomSheetBehavior.STATE_COLLAPSED) {
                    // A downward fling from detail must stop at summary before it can hide.
                    sheet?.isHideable = newState != BottomSheetBehavior.STATE_EXPANDED
                    if (newState == BottomSheetBehavior.STATE_COLLAPSED) controls.scrollTo(0, 0)
                }
                updateSheetLayout()
            }
            override fun onSlide(bottomSheet: View, slideOffset: Float) = Unit
        })
        binding.sheetRestoreArea?.apply {
            setOnClickListener { sheet?.state = BottomSheetBehavior.STATE_COLLAPSED }
            var startY = 0f
            val slop = ViewConfiguration.get(context).scaledTouchSlop
            setOnTouchListener { view, event ->
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> startY = event.rawY
                    MotionEvent.ACTION_UP -> {
                        val distance = startY - event.rawY
                        if (distance > dp(24) || kotlin.math.abs(distance) <= slop) view.performClick()
                    }
                }
                true
            }
        }
    }

    private fun updateSheetLayout() {
        val summary = Rect()
        resultPanel.routeSummary.getDrawingRect(summary)
        resultPanel.root.offsetDescendantRectToMyCoords(resultPanel.routeSummary, summary)
        // Measure the whole summary, including wrapped lines, above the navigation inset.
        val peek = summary.bottom + dp(8) + controls.paddingBottom
        sheet?.let {
            val availableHeight = binding.root.height - statusInset - dp(12)
            if (availableHeight > 0 && it.maxHeight != availableHeight) {
                it.maxHeight = availableHeight
                controls.requestLayout()
            }
            if (it.peekHeight != peek) it.peekHeight = peek
        }
        val sheetVisible = !mapFullscreen && sheet != null && sheet?.state != BottomSheetBehavior.STATE_HIDDEN
        binding.sheetRestoreArea?.visibility = if (!mapFullscreen && sheet?.state == BottomSheetBehavior.STATE_HIDDEN)
            View.VISIBLE else View.GONE
        val bottom = if (sheetVisible) peek
            else (if (binding.topContainer != null) navigationInset else 0) +
                dp(if (!mapFullscreen && sheet != null) 48 else 32)
        val actions = mapPanel.mapActions.layoutParams as FrameLayout.LayoutParams
        if (actions.bottomMargin != bottom + dp(12)) {
            actions.bottomMargin = bottom + dp(12)
            mapPanel.mapActions.layoutParams = actions
        }
        val topCover = if (!mapFullscreen && !topCardMinimized) binding.topContainer?.bottom ?: 0 else statusInset
        val attribution = mapPanel.mapAttribution.layoutParams as FrameLayout.LayoutParams
        if (attribution.topMargin != topCover + dp(4)) {
            attribution.topMargin = topCover + dp(4)
            mapPanel.mapAttribution.layoutParams = attribution
        }
        val bottomCover = if (sheetVisible) peek else
            (if (binding.topContainer != null) navigationInset else 0) +
                (if (!mapFullscreen && sheet != null) dp(48) else 0)
        map?.setVisibleArea(topCover + dp(56), bottomCover + dp(88))
    }

    private fun updateTopCardVisibility() {
        val visibility = if (!mapFullscreen && !topCardMinimized) View.VISIBLE else View.GONE
        binding.topContainer?.visibility = visibility
        toolbar.root.visibility = visibility
        searchCard.root.visibility = visibility
        binding.expandTopCard?.visibility = if (!mapFullscreen && topCardMinimized) View.VISIBLE else View.GONE
        binding.root.requestApplyInsets()
        updateSheetLayout()
    }

    private fun setMapFullscreen(fullscreen: Boolean) {
        mapFullscreen = fullscreen
        val panels = if (fullscreen) View.GONE else View.VISIBLE
        controls.visibility = panels
        binding.navigationScrim?.visibility = panels
        mapPanel.root.layoutParams = (mapPanel.root.layoutParams as ViewGroup.MarginLayoutParams).apply {
            marginEnd = if (fullscreen) 0 else mapEndMargin
        }
        mapPanel.resetMap.setText(if (fullscreen) R.string.ui_exit_fullscreen else R.string.ui_fullscreen)
        updateTopCardVisibility()
        // Keep the SDK view alive so resizing preserves the camera, route and overlays.
        if (Build.VERSION.SDK_INT >= 33) {
            fullscreenBack?.let { onBackInvokedDispatcher.unregisterOnBackInvokedCallback(it) }
            fullscreenBack = if (fullscreen) OnBackInvokedCallback { setMapFullscreen(false) } else null
            fullscreenBack?.let {
                onBackInvokedDispatcher.registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, it)
            }
        }
    }

    @Deprecated("Legacy back handling for Android 12 and earlier")
    @SuppressLint("GestureBackNavigation") // API 33+ uses the registered OnBackInvokedCallback above.
    override fun onBackPressed() {
        if (mapFullscreen) setMapFullscreen(false) else super.onBackPressed()
    }

    private fun loadData() {
        val retained = lastNonConfigurationInstance as? PilotData
        if (retained != null && retained.facilities.isNotEmpty()) {
            data = retained
            bindRoutes(); displayMap()
            if (!workflowAttached) { workflow.attach(restoreState); workflowAttached = true }
            return
        }
        status.text = "파일럿 자료를 불러오는 중…"
        loader.execute {
            val loaded = runCatching {
                fun read(name: String) = assets.open(name).bufferedReader(Charsets.UTF_8).use { it.readText() }
                PilotData.parse(read("pilot-facilities.geojson"), read("result-v2.json"), read("routes-v2.geojson"), read("pilot-security-lights.geojson"))
            }
            handler.post {
                if (isDestroyed) return@post
                loaded.onSuccess {
                    data = (lastNonConfigurationInstance as? PilotData)?.copy(facilities = it.facilities) ?: it
                    bindRoutes(); displayMap()
                    if (!workflowAttached) { workflow.attach(restoreState); workflowAttached = true }
                }.onFailure {
                    status.text = "자료를 불러오지 못했습니다"
                    AlertDialog.Builder(this).setTitle("자료 오류").setMessage(it.message)
                        .setPositiveButton("재시도") { _, _ -> loadData() }.setNegativeButton("닫기", null).show()
                }
            }
        }
    }

    private fun bindRoutes() {
        val routes = data?.routes ?: return
        bindingRoutes = true
        resultPanel.routeSpinner.apply {
            val labels = routes.map {
                    val score = it.safetyScore?.let { value -> String.format(Locale.KOREA, " · %.1f점", value) } ?: ""
                    "${it.title}\n${String.format(Locale.KOREA, "%.0fm · %.1f분", it.distanceMeters, it.estimatedMinutes)}$score${if (it.routeStatus == "incomplete") " · 연결 미완결" else ""}"
                }
            adapter = object : ArrayAdapter<String>(this@MainActivity, 0, labels) {
                override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                    val row = if (convertView == null) ViewRouteOptionBinding.inflate(layoutInflater, parent, false)
                        else ViewRouteOptionBinding.bind(convertView)
                    row.root.text = getItem(position)
                    return row.root
                }
                override fun getDropDownView(position: Int, convertView: View?, parent: ViewGroup): View =
                    getView(position, convertView, parent)
            }
            selected = selected.coerceIn(0, (routes.size - 1).coerceAtLeast(0))
            if (routes.isNotEmpty()) setSelection(selected)
        }
        bindingRoutes = false
    }

    private fun applyServerData(result: PilotData, index: Int) {
        data = result; selected = index.coerceIn(0, (result.routes.size - 1).coerceAtLeast(0))
        bindRoutes()
        preview?.data = result
        map?.replaceData(result)
        refresh()
        controls.post {
            sheet?.state = BottomSheetBehavior.STATE_COLLAPSED
            controls.smoothScrollTo(0, resultPanel.root.top)
        }
    }

    private fun displayMap() {
        val data = data ?: return
        map?.close(); map = null; preview = null
        container.removeAllViews()
        mapPanel.preview.text = if (showLocal && BuildConfig.TMAP_APP_KEY.isNotBlank()) "TMAP 보기" else "로컬 보기"
        if (showLocal) {
            preview = PilotPreviewView(this).also {
                it.data = data
                it.onFacilitiesClick = ::showFacilityGroup
                it.onMapLongPress = { point -> if (workflowAttached) workflow.chooseMapPoint(point) }
                container.addView(it)
            }
            status.text = if (BuildConfig.TMAP_APP_KEY.isBlank()) "앱키 미설정 · 로컬 좌표 미리보기" else "로컬 좌표 미리보기 · 배경지도 없음"
        } else {
            status.text = "TMAP 지도 연결 중 · 지연되면 로컬 보기 사용"
            try {
                map = TmapPilotMap(this, BuildConfig.TMAP_APP_KEY, data,
                    { message -> handler.post { if (!isDestroyed && !showLocal) status.text = message } },
                    { facilities -> handler.post { if (!isDestroyed) showFacilityGroup(facilities) } },
                    { handler.post { if (!isDestroyed && !showLocal) { status.text = "지도 준비 완료"; refresh() } } },
                    { point -> handler.post { if (!isDestroyed && workflowAttached && !showLocal) workflow.chooseMapPoint(point) } })
                container.addView(map!!.view)
                if (resumed) map!!.view.onResume()
            } catch (error: Exception) { mapFailure() }
              catch (error: UnsatisfiedLinkError) { mapFailure() }
        }
        refresh()
        updateSheetLayout()
    }

    private fun mapFailure() {
        map?.close(); map = null
        showLocal = true
        displayMap()
        status.text = "TMAP 초기화 실패 · 로컬 좌표 미리보기"
    }

    private fun visibleKinds() = filters.mapIndexedNotNull { index, filter ->
        kinds[index].takeIf { filter.isChecked }
    }.toSet()

    private fun refresh() {
        val data = data ?: return
        val visible = visibleKinds()
        preview?.apply { selectedRoute = selected; visibleKinds = visible; currentLocation = location; showWeak = this@MainActivity.showWeak; invalidate() }
        map?.update(selected, visible, location, showWeak)
        listOf(resultPanel.scoreValue, resultPanel.averageValue, resultPanel.weakValue).forEach { it.text = "—" }
        resultPanel.gradeLegend.visibility = View.GONE
        resultPanel.scoreHeading.text = "시설 지표"
        resultPanel.routeFacilityCounts.text = "경로 주변 고유 시설 수 · 미조회"
        resultPanel.saveFavorite.isEnabled = data.routes.isNotEmpty()
        resultPanel.routeSpinner.isEnabled = data.routes.isNotEmpty()
        if (data.routes.isEmpty()) {
            resultPanel.routeSummary.text = "현재 입력에 연결된 경로가 없습니다"
            resultPanel.warning.text = "그래프 연결을 임의 생성하지 않습니다 · 다른 보행 지점을 선택하세요"
            return
        }
        val route = data.routes[selected]
        val counts = route.facilityCounts
        resultPanel.routeFacilityCounts.text = "경로 주변 고유 시설 수 · 필터와 무관\n" +
            "CCTV ${counts["cctv"] ?: "—"} · 비상벨 ${counts["emergency_bell"] ?: "—"} · 보안등 ${counts["security_lamp"] ?: "—"}"
        resultPanel.routeSummary.text = String.format(Locale.KOREA,
            "%s · %.0fm · 약 %.1f분\n전용 보행선 %.1f%% · 보유 시설 기록 %d개\n경로 100m 주변 %d개 표시", route.title,
            route.distanceMeters, route.estimatedMinutes, route.pedestrianPercent, data.visibleFacilities(visible).size,
            data.mapFacilities(selected, visible).size)
        resultPanel.scoreHeading.text = when {
            route.safetyScore != null -> "공공시설 기반 안전지표 · 100점 기준"
            route.availableDataScore != null -> "부분 시설지표 · 동일 자료 기준"
            else -> "경로 검색 후 시설지표 확인"
        }
        for ((view, value) in listOf(resultPanel.scoreValue to (route.safetyScore ?: route.availableDataScore),
            resultPanel.averageValue to route.averageSafety, resultPanel.weakValue to route.weakSafety)) {
            view.text = value?.let { String.format(Locale.KOREA, "%.1f", it) } ?: "—"
        }
        val connection = when (route.routeStatus) {
            "already_at_destination" -> "동일 보행 지점 · 이동거리 0"
            "complete" -> "그래프 연결됨 · 실제 보행 가능성 미검증"
            else -> String.format(Locale.KOREA, "연결 미완결 · 도착 지점 간격 %.2fm", data.exitGapMeters)
        }
        resultPanel.gradeLegend.visibility = if (route.safetyScore != null) View.VISIBLE else View.GONE
        val scoreState = if (route.routeStatus == "already_at_destination") "\n이동 없는 경로 · 시설지표 미산출" else ""
        val missing = data.missingTypes.map { kind -> when (kind) {
            "cctv" -> "CCTV"; "emergency_bell" -> "비상벨"; "security_lamp" -> "보안등"
            else -> "이전 기준의 필수 자료"
        } }.distinct()
        val missingState = if (missing.isEmpty()) "" else "\n${missing.joinToString("·")} 자료 미확보 · 부분 시설지표"
        resultPanel.warning.text = "$connection$scoreState$missingState${if (data.savedSnapshot) "\n저장된 과거 결과 · 최신 조회로 확인하세요" else ""}"
    }

    private fun showWeakSegments() {
        val route = data?.routes?.getOrNull(selected) ?: return
        if (route.weakRanges.isEmpty()) { toast("서버 검색 후 지표의 하위 10% 길이 구간을 확인할 수 있습니다"); return }
        showWeak = !showWeak
        refresh()
        if (!showWeak) return
        val lines = route.weakRanges.mapIndexed { index, range ->
            String.format(Locale.KOREA, "%d. %.1fm · 시설지표 %.1f", index + 1, range.lengthMeters, range.score ?: 0.0)
        }
        AlertDialog.Builder(this).setTitle("하위 10% 길이 · 주황색")
            .setMessage("공공시설 기반 안전지표의 하위 구간입니다.\n\n" + lines.take(40).joinToString("\n") +
                if (lines.size > 40) "\n나머지 구간은 지도 표시를 확인하세요" else "")
            .setPositiveButton("닫기", null).show()
    }

    private fun showFacilityGroup(facilities: List<Facility>) {
        if (facilities.size == 1) { showFacility(facilities.first()); return }
        if (facilities.isEmpty()) return
        val groups = summarizeFacilityCluster(facilities)
        val dialogBinding = kr.ac.tukorea.nightsafety.databinding.DialogFacilityClusterBinding.inflate(layoutInflater)
        dialogBinding.clusterTotalBadge.text = "총 ${facilities.size}개"
        dialogBinding.clusterSummarySubtitle.text = groups.joinToString(" · ") { it.summaryText }
        val dialog = AlertDialog.Builder(this).setView(dialogBinding.root).create()
        dialog.window?.setBackgroundDrawableResource(android.R.color.transparent)
        groups.forEach { group ->
            val row = kr.ac.tukorea.nightsafety.databinding.ItemFacilityClusterRowBinding.inflate(
                layoutInflater, dialogBinding.clusterGroupList, false
            )
            row.rowIcon.setImageResource(facilityKindDrawableRes(group.kind))
            row.rowSummary.text = group.summaryText
            row.rowCountBadge.text = "${group.count}개"
            row.root.setOnClickListener {
                dialog.dismiss()
                showFacilityKindGroup(group)
            }
            dialogBinding.clusterGroupList.addView(row.root)
        }
        dialogBinding.clusterClose.setOnClickListener { dialog.dismiss() }
        dialog.show()
    }

    private fun showFacilityKindGroup(group: FacilityKindGroup) {
        if (group.members.size == 1) { showFacility(group.members.first()); return }
        val body = group.members.mapIndexed { index, facility ->
            "[${index + 1}]\n${facility.detail}"
        }.joinToString("\n\n────────────\n\n")
        AlertDialog.Builder(this).setTitle(group.summaryText)
            .setMessage(body)
            .setPositiveButton("닫기", null).show()
    }

    private fun showFacility(facility: Facility) {
        AlertDialog.Builder(this).setTitle(facility.title)
            .setMessage(facility.detail)
            .setPositiveButton("닫기", null).show()
    }

    private fun showDataInfo() {
        val current = data ?: return
        val dates = listOf("cctv" to "CCTV", "bell" to "비상벨", "lamp" to "보안등").map { (kind, label) ->
            val values = current.facilities.filter { it.kind == kind }.mapNotNull { it.dataAsOf }.distinct().sorted()
            "$label 기준일: ${values.joinToString(", ").ifEmpty { "미기록" }}"
        }
        AlertDialog.Builder(this).setTitle("자료 정보")
            .setMessage(dates.joinToString("\n") + "\n\n출처: 시흥시 공공데이터 · 경기데이터드림\n지도 경로: OpenStreetMap 기여자 / ODbL\n\n전체 지표는 경로 평균과 하위 10% 길이의 취약 지표를 함께 반영합니다. 필터는 지도 표시만 바꾸며 점수에는 영향을 주지 않습니다.")
            .setPositiveButton("닫기", null).show()
    }

    private fun showFacilities() {
        val visible = data?.mapFacilities(selected, visibleKinds()) ?: return
        if (visible.isEmpty()) { toast("선택 경로 100m 주변에 표시할 시설이 없습니다"); return }
        AlertDialog.Builder(this).setTitle("경로 100m 주변 시설 ${visible.size}개")
            .setItems(visible.map { it.title }.toTypedArray()) { _, index -> showFacility(visible[index]) }
            .setNegativeButton("닫기", null).show()
    }

    private fun requestLocation() {
        if (checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION), 10)
            return
        }
        val manager = getSystemService(LocationManager::class.java)
        val provider = if (manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) LocationManager.NETWORK_PROVIDER else LocationManager.GPS_PROVIDER
        locationRequest?.cancel()
        try {
            if (Build.VERSION.SDK_INT >= 30) {
                val activeRequest = CancellationSignal()
                locationRequest = activeRequest
                status.text = "현재 위치 확인 중…"
                manager.getCurrentLocation(provider, activeRequest, mainExecutor) { result ->
                    if (isDestroyed || locationRequest !== activeRequest) return@getCurrentLocation
                    locationRequest = null
                    if (result == null) { status.text = "현재 위치를 받지 못했습니다 · 파일럿 선택 유지"; return@getCurrentLocation }
                    location = GeoPoint(result.latitude, result.longitude)
                    status.text = String.format(Locale.KOREA, "현재 위치 정확도 약 %.0fm · 위치는 저장하지 않습니다", result.accuracy)
                    refresh()
                    workflow.useCurrentLocation(location!!)
                }
                handler.postDelayed({
                    if (locationRequest === activeRequest) {
                        activeRequest.cancel()
                        locationRequest = null
                        status.text = "위치 확인 시간 초과 · 파일럿 선택 유지"
                    }
                }, 15_000)
            } else {
                val result = manager.getLastKnownLocation(provider)
                if (result != null && SystemClock.elapsedRealtimeNanos() - result.elapsedRealtimeNanos < 120_000_000_000L) {
                    location = GeoPoint(result.latitude, result.longitude)
                    status.text = "최근 2분 이내 위치 · 실시간 추적 아님"
                    refresh()
                    workflow.useCurrentLocation(location!!)
                } else toast("최근 위치가 없습니다. 파일럿 지도를 계속 이용할 수 있습니다")
            }
        } catch (error: SecurityException) { toast("위치 권한이 없습니다. 파일럿 선택을 유지합니다") }
          catch (error: IllegalArgumentException) { toast("위치 제공자를 사용할 수 없습니다") }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 10) {
            if (checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) requestLocation()
            else toast("위치 권한 없이 파일럿 지도를 이용합니다")
        }
    }

    private fun toast(message: String) = Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("route", selected); outState.putBoolean("local", showLocal)
        outState.putBoolean("map_fullscreen", mapFullscreen)
        outState.putBoolean("top_card_minimized", topCardMinimized)
        filters.forEachIndexed { index, filter -> outState.putBoolean(kinds[index], filter.isChecked) }
        if (workflowAttached) workflow.saveState(outState)
    }
    override fun onResume() { super.onResume(); resumed = true; map?.view?.onResume() }
    @Deprecated("Framework retention is used only for immutable route data; explicit saves use Room")
    override fun onRetainNonConfigurationInstance(): Any? = data
    override fun onPause() {
        resumed = false
        locationRequest?.let { it.cancel(); status.text = "위치 확인 중단 · 파일럿 선택 유지" }
        locationRequest = null
        map?.view?.onPause()
        super.onPause()
    }
    override fun onDestroy() { workflow.close(); map?.close(); handler.removeCallbacksAndMessages(null); loader.shutdownNow(); super.onDestroy() }
}
