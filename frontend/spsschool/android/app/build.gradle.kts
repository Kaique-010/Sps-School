// IMPORTS CORRIGIDOS PARA RESOLVER 'Unresolved reference: util' e 'io'
import java.io.FileInputStream
import java.util.Properties
import java.io.File

// Carrega as propriedades da keystore
// Usamos o 'File' do Kotlin para lidar com caminhos de arquivo de forma mais segura.
val keystorePropertiesFile = rootProject.file("key.properties")
val keystoreProperties = Properties()

if (keystorePropertiesFile.exists()) {
    FileInputStream(keystorePropertiesFile).use { 
        keystoreProperties.load(it) 
    }
}

// Detecta se existe configuração de keystore válida
val hasReleaseKeystore: Boolean = keystorePropertiesFile.exists() &&
    (keystoreProperties.getProperty("storeFile")?.isNotBlank() == true)

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.spsschool.app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    signingConfigs {
        create("release") {
            // Usa o 'File' para garantir que o caminho do arquivo seja tratado corretamente
            val storeFilePath = keystoreProperties.getProperty("storeFile") 
            storeFile = if (storeFilePath != null) File(storeFilePath) else null
            
            storePassword = keystoreProperties.getProperty("storePassword")
            keyAlias = keystoreProperties.getProperty("keyAlias")
            keyPassword = keystoreProperties.getProperty("keyPassword")
        }
    }

    defaultConfig {
        applicationId = "com.spsschool.app"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        getByName("release") {
            // Desativa minify temporariamente para evitar crashes por obfuscação
            isMinifyEnabled = false 
            // Se minify estiver desligado, shrinkResources também deve estar desligado
            isShrinkResources = false
            proguardFiles(getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro")
            // Usa assinatura release se houver keystore; caso contrário, assina com debug
            signingConfig = if (hasReleaseKeystore) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }
        }
    }
}

flutter {
    source = "../.."
}