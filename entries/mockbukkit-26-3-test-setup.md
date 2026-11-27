---
title: "MockBukkit test setup for Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "plugins/SuperiorCrates gradlew test: SuperiorCratesPluginTest (6 tests) passing, 2026-11-24"
sources:
  - "https://repo1.maven.org/maven2/org/mockbukkit/mockbukkit/mockbukkit-v26.3/maven-metadata.xml"
  - "https://github.com/MockBukkit/MockBukkit/issues/1615"
date: 2026-11-24
---

# MockBukkit test setup for Paper 26.3

## Dependencies

```groovy
testImplementation 'io.papermc.paper:paper-api:26.3.build.200-stable'   // not 261, see below
testImplementation 'org.mockbukkit.mockbukkit:mockbukkit-v26.3:4.124.0'
testImplementation platform('org.junit:junit-bom:6.1.3')
testImplementation 'org.junit.jupiter:junit-jupiter'
testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
```

- **Test API build:** MockBukkit 4.124.0 ships registry data for paper-api build **200**. On build 261, `MockBukkit.mock()` fails with `InternalDataLoadException: Null JSON element while retrieving minecraft:world_clock - MockBukkit / MC version mismatch?`. Compile the plugin against 261 (`compileOnly`) and put build 200 on the test classpath. Code that uses an API added after build 200 can only be tested in game.

## Pitfalls

- **Missing classes:** MockBukkit's plugin class loader throws a `NullPointerException` ("No jar file selected") for a missing class, where a real server throws `ClassNotFoundException`. Catch both if the plugin probes for optional classes.
- **Test config files:** write them into `plugin.getDataFolder()` after `MockBukkit.load`, then reload. MockBukkit's `server.getPluginsFolder()/<Name>` is not the plugin's data folder.
- **Async work:** to wait for work that hops back to the main thread with `runTask`, loop on `server.getScheduler().performOneTick()` until the future is done, sleeping a few ms each round. Database threads keep running between ticks.
- **SQLite in tests:** a real SQLite file in a `@TempDir` works, using `org.xerial:sqlite-jdbc:3.49.1.0`, the version Paper bundles.
