import org.jetbrains.kotlin.gradle.dsl.JvmTarget


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
        }
        create("dat") {
            dimension = "frameSource"
            minSdk = 31
            buildConfigField("String", "FRAME_SOURCE", "\"dat\"")
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

    testImplementation(libs.junit)
    testImplementation(libs.json)
}
