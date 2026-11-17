---
title: "Test server settings for bot-swarm performance runs"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "gate_performance runs on 2026-11-17 (50 wandering bots): 3 kicked for flying with allow-flight=false; 0 kicked with allow-flight=true"
sources:
  - "server/logs/latest.log (Paper watchdog thread dump, 2026-11-17 11:19:30)"
date: 2026-11-17
---

# Test server settings for bot-swarm performance runs

## allow-flight

Wandering mineflayer bots get stuck in leaves and vanilla kicks them with `multiplayer.disconnect.flying`. Set `allow-flight=true` in `server/server.properties` on the **test** server only. With it, 50 wandering bots ran 60 s with no kicks.

## Don't trust the first run after a restart

The first 50-bot run right after a restart stalled the main thread for over 10 s (Paper watchdog). The stack was vanilla login code, not a plugin:

```
Connection.syncAfterConfigurationChange -> setupOutboundProtocol
ServerLoginPacketListenerImpl.handleLoginAcknowledgement
```

The main thread waits on the netty thread during each login, and 50 simultaneous logins through ViaVersion/ViaBackwards (bots join as 26.1) with PacketEvents injected backed it up. 19 bots failed to join. An identical run straight afterwards had no stall. Don't save a baseline from the first run after a restart. Run once to warm up, then save.

## Baseline on this machine

Paper 26.3 build 253, ViaVersion and ViaBackwards 5.12.2, PacketEvents 2.14.0, CreatePaper skeleton (no listeners or tasks), 50 wandering bots, 60 s: median 28.6 ms/tick, p95 52.8 ms, worst tick 2,036 ms. Idle: 0.7 ms. Saved as baseline `createpaper-skeleton`. Most of the load is probably chunk generation as bots wander (not profiled). Pre-generating the test world would make baselines steadier.
