---
title: "Per-player animations, holograms and hitboxes with display entities on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/phase2-opening/idle-hologram-clear.png, t01-ring.png to t08.png, reveal-above-lid.png; gate_performance (20 bots, median 16.8 ms vs 17.8 baseline), gate_memory and gate_thread_safety pass (2026-11-24)"
sources:
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Entity.html#setVisibleByDefault(boolean)"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Player.html#hideEntity(org.bukkit.plugin.Plugin,org.bukkit.entity.Entity)"
date: 2026-11-24
---

# Per-player animations, holograms and hitboxes with display entities

## Shown to one player only

- **Private entities:** spawn with `setVisibleByDefault(false)` inside the spawn consumer, so nobody ever sees them. Then call `player.showEntity(plugin, entity)`. Used for the opener's copy of the crate model and the reward reveal.
- **Hiding shared entities:** `player.hideEntity(plugin, entity)` on each shared display, then `showEntity` when the opener's animation ends. Each player sees their own opening, and several players can open one crate at once.
- **Particles:** `player.spawnParticle(particle, x, y, z, 1, 0, 0, 0, 0, data)` sends to that one player. `Particle.DUST` needs `new Particle.DustOptions(Color, size)`. Dust lingers about a second, so an expanding ring drawn every tick reads as a filled, spreading area rather than a thin ring.

## Hologram

A single `TextDisplay` with lines joined by `JoinConfiguration.newlines()`, billboard CENTER, `setDefaultBackground(false)` and `setShadowed(true)`. MiniMessage gradients and hex colours render as written, and ★/☆ render in the vanilla font.

## Clickable model

- **Hitbox:** a model standing on air has no block to click. Put an `Interaction` entity at its base with `setInteractionWidth` and `setInteractionHeight` and `setResponsive(true)`, tagged in its PDC with the placement.
- **Event:** right-clicks arrive as `PlayerInteractEntityEvent` with `getRightClicked() instanceof Interaction`. Check `getHand() == EquipmentSlot.HAND` to avoid the second off-hand event. A real keyed opening through this path was stored and delivered at the reveal in game.

## Lifecycle

- **No orphans:** every display, text and interaction entity is `setPersistent(false)`, so a crash leaves nothing behind.
- **Chunks:** spawn visuals for placements in loaded chunks on enable and reload. Then follow `ChunkLoadEvent` and `ChunkUnloadEvent`.
- **One ticker:** a single repeating task drives every active session and cancels itself when none remain. Sessions end on finish, on quit and on plugin disable. Ending a session delivers its reward, or leaves the reward PENDING if the player is offline.

## Not yet proven

- Sneak-to-skip, which the client tools can't press.
- Behaviour with many simultaneous sessions under load: the gate bots can't open placed crates.
- Visibility after the opener changes world mid-animation.
