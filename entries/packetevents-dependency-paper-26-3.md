---
title: "Depending on PacketEvents 2.14.0 from a Paper 26.3 plugin"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/plugin-skeleton/status-both-dependencies.png; server log 'Loaded packetevents v2.14.0' and 'Loading block mappings for V_26_3' on Paper 26.3 build 253"
sources:
  - "https://github.com/retrooper/packetevents/releases/tag/v2.14.0"
  - "https://repo.codemc.io/repository/maven-releases/com/github/retrooper/packetevents-spigot/maven-metadata.xml"
date: 2026-11-17
---

# Depending on PacketEvents 2.14.0 from a Paper 26.3 plugin

PacketEvents 2.14.0 is the first release that supports 26.3 (protocol 777). The standalone `packetevents-spigot-2.14.0.jar` loads on Paper 26.3 build 253 and logs `Loading block mappings for V_26_3`.

## Setup

- Run it as its own plugin in `server/plugins/`; don't shade it (an anticheat may ship its own copy).
- Gradle: repository `https://repo.codemc.io/repository/maven-releases/`, `compileOnly 'com.github.retrooper:packetevents-spigot:2.14.0'`.
- `plugin.yml`: `depend: [packetevents]` (the plugin name is lowercase).

## Pitfalls

- PacketEvents checks GitHub for updates at startup ("Checking for updates, please wait..."). The standalone jar didn't create a config file for it; turning it off is still to be done from our plugin's PacketEvents settings.
- Only loading is proven here. Sending packets (display entities, metadata indices) is still in `research/PacketEvents on Paper 26.3.md`.
