
plugins {
    application
    kotlin("jvm")
    id("com.github.johnrengelman.shadow")
}

group = "com.linole"
version = "1.0.0"
application {
    mainClass.set("io.ktor.server.netty.EngineMain")
    val isDevelopment: Boolean = project.ext.has("development")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=$isDevelopment")
}

repositories {
    mavenCentral()
    maven {
        name = "GitHubPackages"
        url = uri("https://maven.pkg.github.com/ole-klokkhammer/linole")
        credentials {
            username = System.getenv("GITHUB_USERNAME")
            password = System.getenv("GITHUB_TOKEN")
        }
    }
}

dependencies {
    implementation(Kotlin.stdlib.jdk8)
    implementation(Ktor.server.core)
    implementation(Ktor.features.jackson)
    implementation(Koin.ktor)
    implementation(Ktor.server.netty)
    implementation("ch.qos.logback:logback-classic:_")
    implementation("com.linole:mqtt-client:_")
}

tasks {
    shadowJar {
        manifest {
            attributes(Pair("Main-Class", "io.ktor.server.netty.EngineMain"))
        }
    }
}