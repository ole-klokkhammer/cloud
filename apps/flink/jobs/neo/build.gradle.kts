// https://nightlies.apache.org/flink/flink-docs-master/docs/dev/configuration/overview/#getting-started

repositories {
    mavenCentral()
    maven {
        url = uri("https://repository.apache.org/content/repositories/snapshots")
        mavenContent {
            snapshotsOnly()
        }
    }
}

plugins {
    java
    application
    id("com.github.johnrengelman.shadow") version "7.1.2"
    kotlin("jvm")
}

group = "com.olklokk.flink.neo"
version = "1.0-SNAPSHOT"
description = "Flink Quickstart Job"

val flinkVersion = "2.0.0"
val kafkaConnector = "4.0.0-2.0"

application {
    mainClass.set("com.olklokk.flink.neo.MainKt")
    applicationDefaultJvmArgs = listOf("-Dlog4j.configurationFile=log4j2.properties")
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("org.apache.flink:flink-streaming-java:$flinkVersion")
    implementation("org.apache.flink:flink-clients:$flinkVersion")
    implementation("org.apache.flink:flink-connector-kafka:$flinkVersion")
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
}

configurations {
    val flinkShadowJar by creating {
        exclude(group = "org.apache.flink", module = "force-shading")
        exclude(group = "com.google.code.findbugs", module = "jsr305")
        exclude(group = "org.slf4j")
        exclude(group = "org.apache.logging.log4j")
    }
}

sourceSets {
    named("main") {
        compileClasspath += configurations["flinkShadowJar"]
        runtimeClasspath += configurations["flinkShadowJar"]
    }
    named("test") {
        compileClasspath += configurations["flinkShadowJar"]
        runtimeClasspath += configurations["flinkShadowJar"]
    }
}

tasks.named<JavaExec>("run") {
    classpath = sourceSets["main"].runtimeClasspath
}

tasks.named<Jar>("jar") {
    manifest {
        attributes(
            "Built-By" to System.getProperty("user.name"),
            "Build-Jdk" to System.getProperty("java.version")
        )
    }
}

tasks.named<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar>("shadowJar") {
    configurations = listOf(project.configurations["flinkShadowJar"])
}