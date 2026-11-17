---
title: "MockBukkit needs the Paper API build it was built against"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "plugins/createpaper CreatePaperPluginTest (4 tests pass with paper-api 26.3.build.200-stable; all 4 fail with 26.3.build.253-stable)"
sources:
  - "mockbukkit-v26.3-4.120.0.jar META-INF/MANIFEST.MF (Paper-Version: 26.3.build.200-stable)"
  - "https://repo1.maven.org/maven2/org/mockbukkit/mockbukkit/mockbukkit-v26.3/maven-metadata.xml"
date: 2026-11-17
---

# MockBukkit needs the Paper API build it was built against

MockBukkit ships registry data for one Paper build. If the tests run against a newer `paper-api`, `MockBukkit.mock()` fails before any test runs:

```
InternalDataLoadException: Null JSON element while retrieving `minecraft:world_clock` - MockBukkit / MC version mismatch?
```

Paper 26.3 build 253 added the `minecraft:world_clock` registry; `mockbukkit-v26.3:4.120.0` was built against build 200 and has no data for it.

## Fix

Compile the plugin against the server's build, and run the tests against MockBukkit's build:

```groovy
def paperApi = '26.3.build.253-stable'          // from server/libraries
def paperApiForTests = '26.3.build.200-stable'  // MockBukkit's Paper-Version
dependencies {
    compileOnly "io.papermc.paper:paper-api:${paperApi}"
    testImplementation "io.papermc.paper:paper-api:${paperApiForTests}"
    testImplementation 'org.mockbukkit.mockbukkit:mockbukkit-v26.3:4.120.0'
}
```

Find MockBukkit's build in its jar's `META-INF/MANIFEST.MF` (`Paper-Version`). Raise `paperApiForTests` when a newer MockBukkit release moves it.

Pitfall: API added between the two builds compiles in `main` but not in tests. That shows up as a test compile error, not a silent difference.
