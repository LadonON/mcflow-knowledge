---
title: "BetterModel 3.6.0 load order and telemetry settings on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/plugin-skeleton/status-both-dependencies.png; server logs before and after adding softdepend (2026-11-17 11:28 and 11:30)"
sources:
  - "bettermodel-3.6.0-paper.jar running on Paper 26.3 build 253"
  - "server/plugins/BetterModel/config.yml"
date: 2026-11-17
---

# BetterModel 3.6.0 load order and telemetry settings on Paper 26.3

BetterModel 3.6.0 runs as a **Paper plugin** (`paper-plugin.yml`). It logs `Minecraft version: 26.3.0, NMS version: V26_R3` on Paper 26.3 build 253.

## Load order

A Bukkit plugin that looks BetterModel up in `onEnable` won't find it enabled unless it declares the dependency. Without it, the log showed `CreatePaper Enabling` before `BetterModel Enabling`, and `isEnabled()` was false.

Fix in our `plugin.yml`:

```yaml
softdepend: [BetterModel]   # or depend: once BetterModel is required
```

After that, BetterModel enables first.

BetterModel finishes loading its models a few seconds **after** it enables (`Enabling` at 11:30:38, `Plugin is loaded. (2,084 ms)` at 11:30:42). Code that uses BetterModel's model API must wait for that, not just for `onEnable`. Which event or callback signals it is still unproven.

## Telemetry

`plugins/BetterModel/config.yml` has `metrics: true` (bStats) and `version-check: true` (GitHub, and it messages ops in chat about new snapshots). Both send data out, so both are set to `false` on the test server, as `CLAUDE.md` requires.
