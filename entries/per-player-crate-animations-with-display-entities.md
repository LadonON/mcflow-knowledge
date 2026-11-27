---
title: "Per-player animations, holograms and hitboxes with display entities on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/phase2-opening/idle-hologram-clear.png, t01-ring.png to t08.png, reveal-above-lid.png; gate_performance (20 bots, median 16.8 ms vs 17.8 baseline), gate_memory and gate_thread_safety pass (2026-11-24); server/screenshots/phase2-finish/roulette-*.png, showcase-*.png, visuals-row-day.png; bot sneak-skip (reward delivered 2.5 s into a 5 s roulette); hitbox sizes read back with /data (2026-11-25)"
sources:
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Entity.html#setVisibleByDefault(boolean)"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Player.html#hideEntity(org.bukkit.plugin.Plugin,org.bukkit.entity.Entity)"
date: 2026-11-25
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

## Skipping

- **Sneak:** `PlayerToggleSneakEvent` with `isSneaking()` jumps the session to its skip tick. Proven with a bot: the reward landed about 2.5 s into a roulette that stops at 5 s.
- **Long steps** (a roulette, a showcase) work out their state from the time since they started, so a jump just lands on the right frame. Steps they skip over still run once, at their own tick, so they set up (spawn) correctly.
- **A model animation** isn't held for the skip. Seek it to `(skip tick - its start tick)` so it is where it would naturally be.

## Hitbox from bounds

For a crate standing on air, size the `Interaction` to cover every part:

- **Model:** twice the furthest cube corner from the vertical axis on X or Z, by top minus base (cube rotations ignored). The legendary crate measures 2.06 x 1.51.
- **Block display:** 1 x 1 x scale.
- **Item display:** 0.5 x 1 x scale.
- **Entity:** its own width and height.
- **Offsets:** an offset part adds 2 x its sideways reach to the width and its height offset to the height. A hologram-only crate gets 1 x 1.

## Labels

A `TextDisplay`'s position is the **bottom** of its text. To put a label's top at a height, anchor it one line (0.25 blocks at scale 1) lower. Use `setDefaultBackground(false)` and a transparent background colour for floating labels; the default is a grey box.

## Commands as a player from the console

Read the player from `CommandSourceStack#getExecutor()`, not `getSender()`. Then `/execute as <player> run sc ...` works from the console or command blocks.

## Not yet proven

- Visibility after the opener changes world mid-animation.
- Cubes rotated on more than one axis (no model in use has any).
