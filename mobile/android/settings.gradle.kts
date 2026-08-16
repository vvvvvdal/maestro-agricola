import java.util.Properties


pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

val localProperties = Properties().apply {
    val localFile = file("local.properties")
    if (localFile.exists()) localFile.inputStream().use(::load)
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://maven.pkg.github.com/facebook/meta-wearables-dat-android")
            credentials {
                username = ""
                password = System.getenv("GITHUB_TOKEN") ?: localProperties.getProperty("github_token", "")
            }
        }
    }
}

rootProject.name = "MaestroAgricola"
include(":app")
