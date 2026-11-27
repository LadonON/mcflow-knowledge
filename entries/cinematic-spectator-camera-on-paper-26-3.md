---
title: "Cinematic camera with a spectator target and a full-screen fade glyph on Paper 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/phase2-finish/cinematic-fade.png, cinematic-scene.png, cinematic-cycle.png, reverify-cinematic.png, cinematic-on-crate-winner.png; restart mid-cinematic restored game mode 3 -> 0 and position (2026-11-25); CinematicTest (7 tests); gate_resource_pack pass on resourcepacks/superiorcrates"
sources:
  - "research/Cinematic Camera Control on Paper 26.3.md (paper-api and client jar, javap)"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Player.html#setSpectatorTarget(org.bukkit.entity.Entity)"
date: 2026-11-25
---

# Cinematic camera with a spectator target and a full-screen fade glyph

Proven with SuperiorCrates' cinematic opening: the screen fades to black, the view moves to a scene elsewhere in the world, the HUD disappears, and the player is put back exactly where they were.

## Camera

- **Spectator only:** `Player#setSpectatorTarget` throws unless the player is in `GameMode.SPECTATOR`. Switch them, teleport them to the camera spot (so the scene's chunks and entities load for them), then spectate.
- **Camera entity:** an empty `ItemDisplay` spawned with `setVisibleByDefault(false)` plus `showEntity` for the viewer. Wait **2 ticks** after spawning before `setSpectatorTarget`, or the client ignores a camera it hasn't received yet. Do both while the screen is black.
- **Facing:** the camera takes the display's yaw and pitch from its spawn and teleport location.
- **HUD:** while spectating the display there's no hotbar, hearts, food, crosshair or hand. Chat and titles still show.
- **Moving it:** teleport the display every tick with `setTeleportDuration(1)`. A 1-block drift over 3 s looked steady in game. Smoothness wasn't measured beyond that.

## Keeping the player on the camera

- **Sneak:** cancel `PlayerToggleSneakEvent` (LOWEST) for players behind a camera, or the server drops the camera. A listener that should still react to the sneak (a skip) must not use `ignoreCancelled = true`.
- **Other exits:** cancel `PlayerTeleportEvent` with cause `SPECTATE` (the spectator menu). Cancel `PlayerStartSpectatingEntityEvent` for any other target and `PlayerStopSpectatingEntityEvent` for the camera. These events live in `com.destroystokyo.paper.event.player`, not `io.papermc.paper.event.player`.

## Never stranding a player

- **Before switching:** store game mode, location, `getAllowFlight`, `isFlying` and `getFlySpeed` in the player's PDC.
- **Restoring:** `setSpectatorTarget(null)`, then `setGameMode(saved)`, then restore flight (a game-mode change wipes it), then teleport. Remove the PDC entry.
- **When to restore:** at the end, on quit, on plugin disable (proven: a restart mid-cinematic put the player back in survival at their spot), and on join if the PDC entry is still there (crash). The join path is unit-tested only; a killed server process wasn't tried.

## Fade to black (pack format 97)

- **Font:** one bitmap glyph, a **4x1 solid-black PNG** with `height: 512` and `ascent: 253`. It's drawn 2048 units wide and the title scales it x4, so it covers 8192x2048 GUI px. Ascent = height/2 - 3 centres it on the title line (glyph top = -10 + 7 - ascent units from the centre).
- **Sending:** `Title.title(Component.text("").font(Key.key(ns, "fade")), empty, Times(10, 10, 10 ticks))`. The client fades the glyph's alpha, so the screen darkens and clears smoothly.
- **Coverage:** proven only at a 1920x1174 window with GUI scale Auto. Other GUI scales and ultrawide aren't checked.
- **Pack:** the gate accepts `ascent <= height` at this size.

## Rewards on the open crate

- **Timing:** the reward cycle is timed to the crate model's own lid-open window (1.2–3.1 s for the legendary crate). The cycle starts when the lid is open, and the winner lands with a third of the window left. It's removed 2 ticks before the lid starts closing, so the model's animation never has to be held.
- **Placement:** the item floats 1.6 blocks above the crate's base, billboard VERTICAL, with the name's text display anchored just above the item's top.
- **Size:** an `ItemDisplay` at scale 1 drew a sword about 0.85 blocks tall from 3 blocks away. Size items for that, not for half a block.

## Pitfalls

- A text display's anchor is the **bottom** of its text: to put a label's top at a given height, anchor it one line (0.25 blocks at scale 1) lower.
