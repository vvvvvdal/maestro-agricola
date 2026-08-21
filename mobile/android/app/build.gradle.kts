import org.jetbrains.kotlin.gradle.dsl.JvmTarget


val datMockDeviceEnabled = providers.gradleProperty("maestroDatMockDevice")
    .map { it.toBooleanStrict() }
    .getOrElse(false)
val datMockScenario = providers.gradleProperty("maestroDatMockScenario")
    .getOrElse("success")
val allowedDatMockScenarios = setOf("success", "permission-denied", "timeout", "disconnect")
require(datMockScenario in allowedDatMockScenarios) {
    "maestroDatMockScenario deve ser um de: ${allowedDatMockScenarios.joinToString()}"
}


plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android)
    alias(libs.plugins.compose.compiler)
}

android {
    namespace = "br.org.agroturtles.maestro"
    compileSdk = 36

    defaultConfig {
        applicationId = "br.org.agroturtles.maestro"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        manifestPlaceholders["mwdat_application_id"] = ""
        manifestPlaceholders["mwdat_client_token"] = ""
    }

    flavorDimensions += "frameSource"
    productFlavors {
        create("mock") {
            dimension = "frameSource"
            minSdk = 26
            applicationIdSuffix = ".mock"
            versionNameSuffix = "-mock"
            buildConfigField("String", "FRAME_SOURCE", "\"mock\"")
            buildConfigField("boolean", "DAT_MOCK_DEVICE", "false")
            buildConfigField("String", "DAT_MOCK_SCENARIO", "\"not-applicable\"")
        }
        create("dat") {
            dimension = "frameSource"
            minSdk = 31
            val sourceLabel = if (datMockDeviceEnabled) {
                "dat-mockdevice:$datMockScenario"
            } else {
                "dat"
            }
            buildConfigField("String", "FRAME_SOURCE", "\"$sourceLabel\"")
            buildConfigField("boolean", "DAT_MOCK_DEVICE", datMockDeviceEnabled.toString())
            buildConfigField("String", "DAT_MOCK_SCENARIO", "\"$datMockScenario\"")
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    packaging.resources.excludes += "/META-INF/{AL2.0,LGPL2.1}"

    sourceSets {
        getByName("main").assets.srcDir("../../../shared/ai")
        getByName("main").assets.srcDir("../../../robot_ws/src/maestro_robot_bridge/config")
        getByName("test").resources.srcDir("../../../shared/ai")
        getByName("test").resources.srcDir("../../../shared/target")
        getByName("dat").assets.srcDir(
            "../../../robot_ws/src/maestro_simulation/models/plot_marker/materials/textures"
        )
    }
}

kotlin {
    compilerOptions.jvmTarget = JvmTarget.JVM_17
}

dependencies {
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.material3)
    implementation(libs.okhttp)

    "datImplementation"(libs.mwdat.core)
    "datImplementation"(libs.mwdat.camera)
    "datImplementation"(libs.mwdat.mockdevice)
    "datImplementation"(libs.zxing.core)

    testImplementation(libs.junit)
    testImplementation(libs.json)
    testImplementation(libs.zxing.core)
}
