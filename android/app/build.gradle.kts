plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("com.chaquo.python") }

android {
    namespace = "org.fuorigiri.performancelab"
    buildFeatures { buildConfig = true }
    compileSdk = 35
    defaultConfig {
        applicationId = "org.fuorigiri.performancelab"
        minSdk = 26
        targetSdk = 35
        versionCode = 800
        versionName = "0.8.0"
        ndk { abiFilters += listOf("arm64-v8a", "x86_64") }
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    sourceSets.getByName("main") {
        assets.srcDir("../../frontend/dist")
    }
    packaging { jniLibs { useLegacyPackaging = false } }
    buildTypes { getByName("release") { isMinifyEnabled = false } }
}
chaquopy {
    defaultConfig {
        version = "3.13"
        pip {
            options("--find-links", "${rootProject.projectDir}/wheels")
            install("-r", "${rootProject.projectDir}/requirements.txt")
        }
    }
    sourceSets { getByName("main") { srcDir("../../backend") } }
}
dependencies {
    implementation("com.google.android.gms:play-services-auth:22.0.0")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.webkit:webkit:1.13.0")
    implementation("androidx.work:work-runtime-ktx:2.10.1")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
