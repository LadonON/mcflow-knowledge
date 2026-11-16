---
title: "MockBukkit 4.120.0 needs paper-api 26.3 build 200 for tests"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "plugins/PayPing ToastManagerTest (5 MockBukkit tests pass on build 200; all failed on build 253)"
sources:
  - "https://github.com/MockBukkit/MockBukkit/blob/v4.120.0/gradle.properties (paper.api.full-version=26.3.build.200-stable)"
  - "https://repo1.maven.org/maven2/org/mockbukkit/mockbukkit/mockbukkit-v26.3/maven-metadata.xml"
date: 2026-11-16
---

# MockBukkit 4.120.0 needs paper-api 26.3 build 200 for tests

- `org.mockbukkit.mockbukkit:mockbukkit-v26.3:4.120.0` (the latest, Nov 2026)
  fails in `MockBukkit.mock()` against `paper-api:26.3.build.253-stable` with
  `InternalDataLoadException: Null JSON element while retrieving minecraft:world_clock`.
- It was built against `26.3.build.200-stable`. Compile the plugin against the
  server's build, and put build 200 on the test classpath only:

```groovy
compileOnly 'io.papermc.paper:paper-api:26.3.build.253-stable'
testImplementation 'io.papermc.paper:paper-api:26.3.build.200-stable'
testImplementation 'org.mockbukkit.mockbukkit:mockbukkit-v26.3:4.120.0'
testImplementation 'org.junit.jupiter:junit-jupiter:6.1.3'
testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
```

- `PlayerMock.activeBossBars()` returns an `Iterable`, not a collection.
- Gradle 9.8.2 with a Java 25 toolchain works.
