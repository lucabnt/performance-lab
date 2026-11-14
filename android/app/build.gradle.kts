plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("com.chaquo.python") }

android {
    namespace = "org.fuorigiri.performancelab"
    buildFeatures { buildConfig = true }
    compileSdk = 35
    defaultConfig {
        applicationId = "org.fuorigiri.performancelab"
        minSdk = 26
        targetSdk = 35
        versionCode = 1000
        versionName = "0.10.0"
        ndk { abiFilters += listOf("arm64-v8a", "x86_64") }
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    sourceSets.getByName("main") {
        assets.srcDir("../../frontend/dist")
    }
    sourceSets.getByName("androidTest") {
        assets.srcDir(layout.buildDirectory.dir("generated/pillowRuntimeCheck"))
    }
    packaging { jniLibs { useLegacyPackaging = false } }
    buildTypes { getByName("release") { isMinifyEnabled = false } }
}
val preparePillowRuntimeCheck by tasks.registering(Copy::class) {
    from("../../scripts/check_android_pillow_runtime.py")
    into(layout.buildDirectory.dir("generated/pillowRuntimeCheck"))
}
tasks.matching { it.name.startsWith("merge") && it.name.endsWith("AndroidTestAssets") }.configureEach {
    dependsOn(preparePillowRuntimeCheck)
}
chaquopy {
    defaultConfig {
        version = "3.13"
        pip {
            options("--find-links", "${rootProject.projectDir}/wheels")
            install("-r", "${rootProject.projectDir}/requirements.txt")
            val sharedWheel = file("${rootProject.projectDir}/../requirements-common.txt").readLines().first { it.startsWith("vendor/") }
            install("${rootProject.projectDir}/../$sharedWheel")
        }
    }
    sourceSets { getByName("main") { srcDir("../../backend") } }
}
// --find-links directories are otherwise not tracked when local wheels change.
tasks.matching { it.name.startsWith("install") && it.name.endsWith("PythonRequirements") }.configureEach {
    inputs.files(fileTree("${rootProject.projectDir}/wheels") {
        include("*.whl", "SHA256.json")
    })
    // PEP 610 metadata of the local shared wheel records the builder checkout path.
    // The wheel stays installed from the reviewed file (no name lookup on an index).
    doLast {
        outputs.files.forEach { output ->
            output.walkTopDown().filter { it.isFile && it.name == "direct_url.json" }.forEach { it.delete() }
        }
    }
}
dependencies {
    implementation("com.google.android.gms:play-services-auth:22.0.0")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.webkit:webkit:1.13.0")
    implementation("androidx.work:work-runtime-ktx:2.10.1")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
