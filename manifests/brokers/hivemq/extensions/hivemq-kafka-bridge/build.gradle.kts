plugins {
    kotlin("jvm") version "2.1.10"
    alias(libs.plugins.hivemq.extension)
    alias(libs.plugins.license)
}

group = "com.hivemq.extensions"
version = "1.0-SNAPSHOT"

hivemqExtension {
    name = "Mqtt to Kafka Bridge"
    author = "Me"
    priority = 1000
    startPriority = 1000
    mainClass = "$group.linole.Main"
    sdkVersion = libs.versions.hivemq.extension.sdk
    version = project.version.toString()

    resources {
        from("LICENSE")
    }
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation(libs.kafka.client)
}

license {
    header = rootDir.resolve("HEADER")
    mapping("java", "SLASHSTAR_STYLE")
}

kotlin {
    jvmToolchain(15)
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(15))
    }
}