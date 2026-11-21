import java.util.Properties

plugins { id("com.android.application") }

val local = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) file.inputStream().use { load(it) }
}
val mapKey = local.getProperty("TMAP_APP_KEY", "").trim()
val apiBaseUrl = local.getProperty("API_BASE_URL", "http://127.0.0.1:8765").trim()
require(listOf(mapKey, apiBaseUrl).all { value -> value.none { it.isISOControl() } }) { "앱 설정에 허용되지 않는 제어문자가 있습니다" }

android {
    namespace = "kr.ac.tukorea.nightsafety"
    compileSdk = 36
    defaultConfig {
        applicationId = "kr.ac.tukorea.nightsafety"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
        buildConfigField("String", "TMAP_APP_KEY", "\"${mapKey.replace("\\", "\\\\").replace("\"", "\\\"")}\"")
        buildConfigField("String", "API_BASE_URL", "\"${apiBaseUrl.replace("\\", "\\\\").replace("\"", "\\\"")}\"")
        testInstrumentationRunner = "android.test.InstrumentationTestRunner"
    }
    buildFeatures { buildConfig = true; viewBinding = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    sourceSets.getByName("test").resources.srcDir("src/main/assets")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.1")
    annotationProcessor("androidx.room:room-compiler:2.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation(files("libs/tmap-sdk-3.7.aar", "libs/vsm-tmap-sdk-v2-eaa-2.0.14.aar"))
    implementation("com.google.flatbuffers:flatbuffers-java:24.3.25")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
