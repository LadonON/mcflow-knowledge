---
title: "Gradle setup for a Paper 26.3 plugin with runtime libraries"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "plugins/SuperiorCrates deployed on Paper 26.3 build 261 (server log 2026-11-24 10:47 and 11:03); server/screenshots/scaffold-smoke-test/sc-alias-reply.png"
sources:
  - "https://repo.papermc.io/repository/maven-public/io/papermc/paper/paper-api/maven-metadata.xml"
  - "https://docs.papermc.io/paper/dev/getting-started/paper-plugins"
  - "server/paper-26.3-261.jar: META-INF/libraries.list"
date: 2026-11-24
---

# Gradle setup for a Paper 26.3 plugin with runtime libraries

## What works

- **Gradle 9.9.2** (Groovy DSL) on **Java 25.0.4**, with the toolchain set to `JavaLanguageVersion.of(25)`.
- **paper-api:** `io.papermc.paper:paper-api:26.3.build.261-stable` from `https://repo.papermc.io/repository/maven-public/`, declared `compileOnly`. Pin the build. The metadata's "latest" is a `26.3-pre-2` alpha.
- **Shadow:** `com.gradleup.shadow` **9.6.1** builds the single deploy jar. Set `jar { enabled = false }`, give `shadowJar` an empty classifier, and make `assemble.dependsOn shadowJar`. `plugin_deploy` picks the one jar in `build/libs`.
- **Multi-module:** an `api` subproject with `implementation project(':api')` in the root, which is shaded into the jar.
- **plugin.yml:** `api-version: '26.3'` is accepted.

## Runtime libraries

- **What loads:** the `plugin.yml` `libraries:` list loads HikariCP 7.1.0, mariadb-java-client 3.5.11 and postgresql 42.7.15. That includes their transitive dependencies: slf4j-api, checker-qual.
- **Where they come from:** Paper downloads them on the first start from `https://maven-central.storage-download.googleapis.com/maven2/` and caches them in `server/libraries/`. Production hosts need outbound access to that mirror for the first start.
- **Already bundled:** Paper 26.3 bundles **sqlite-jdbc 3.49.1.0** and **mysql-connector-j 9.2.0**. A plugin sees both through `DriverManager.getDrivers()` and `Class.forName` without shading or listing them.

## Pitfalls

- **Build output:** the Gradle 9.9.2 build prints JDK warnings about `sun.misc.Unsafe` (ByteBuddy, from MockBukkit) and `System::load` (sqlite-jdbc in tests). They come from test dependencies, not the plugin, and are harmless.
- **BOM from PowerShell:** Windows PowerShell 5.1's `Set-Content -Encoding utf8` writes a BOM, and javac rejects it with `illegal character '﻿'`. Write sources with `[IO.File]::WriteAllText(path, text, New-Object Text.UTF8Encoding($false))`.
