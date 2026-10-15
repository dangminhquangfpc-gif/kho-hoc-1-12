import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

val uploadProperties = Properties()
val uploadPropertiesFile = rootProject.file("key.properties")
// Engineering builds always ignore local signing files, including on a release workstation.
val engineeringBuild = providers.gradleProperty("tuhocEngineering").orNull == "true"
val requireUploadSigning = providers.gradleProperty("tuhocRequireUploadSigning").orNull == "true"
val useUploadSigning = uploadPropertiesFile.exists() && !engineeringBuild
if (useUploadSigning) {
    FileInputStream(uploadPropertiesFile).use { uploadProperties.load(it) }
    listOf("keyAlias", "keyPassword", "storeFile", "storePassword").forEach { name ->
        require(!uploadProperties.getProperty(name).isNullOrBlank()) {
            "Android upload signing is missing a required property: $name"
        }
    }
    require(uploadProperties.getProperty("keyAlias") != "androiddebugkey") {
        "A debug signing key cannot be used for upload signing."
    }
    val uploadStoreFile = file(uploadProperties.getProperty("storeFile"))
    require(uploadStoreFile.isFile && uploadStoreFile.name != "debug.keystore") {
        "Configure a private upload keystore outside Git."
    }
}
require(!requireUploadSigning || (useUploadSigning && !engineeringBuild)) {
    "A store build requires private Android upload signing."
}
gradle.taskGraph.whenReady {
    if (allTasks.any { it.name.endsWith("Release") } && !useUploadSigning && !engineeringBuild) {
        throw GradleException(
            "Choose private upload signing or an explicit unsigned engineering build: " +
                "ORG_GRADLE_PROJECT_tuhocEngineering=true. Engineering AABs cannot be uploaded to Play."
        )
    }
}

android {
    namespace = "vn.khohoc.kho_hoc_mobile"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        // Stable application ID: changing it creates a separate app and breaks upgrade continuity.
        applicationId = "vn.khohoc.kho_hoc_mobile"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = maxOf(24, flutter.minSdkVersion)
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (useUploadSigning) {
            create("upload") {
                keyAlias = uploadProperties.getProperty("keyAlias")
                keyPassword = uploadProperties.getProperty("keyPassword")
                storeFile = file(uploadProperties.getProperty("storeFile"))
                storePassword = uploadProperties.getProperty("storePassword")
            }
        }
    }
    buildTypes {
        release {
            // No debug-signing fallback. Engineering mode ignores local signing files.
            if (useUploadSigning) signingConfig = signingConfigs.getByName("upload")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

flutter {
    source = "../.."
}
