---
title: "Frozen view with live mouse input via a client-only seat and camera (PacketEvents) on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/phase3-frozen-view/step3-camera-only.png, step4-seated.png, step4-after-rotate.png, step7-client-spectator.png, step11-panel-open.png, step12-restored.png, step12-rejoin-after-kick.png; FrozenViewProbe packet logs and a panel test with the user's real mouse (2026-11-26)"
sources:
  - "research/Frozen-View Cursor with PacketEvents on 26.3.md (26.3 client and server jars, javap)"
  - "https://github.com/retrooper/packetevents/releases/tag/v2.14.0"
date: 2026-11-26
---

# Frozen view with live mouse input via a client-only seat and camera

Proven with PacketEvents 2.14.0 (a separate plugin) and ViaVersion 5.12.2 on Paper 26.3, with a real player moving a real mouse.

## Recipe

All of these packets go to the one player only; nothing exists on the server.

1. **Spawn** two client-only `ITEM_DISPLAY` entities with `WrapperPlayServerSpawnEntity`: a seat at the player's feet and a camera at eye height. Use ids far above anything the server hands out (count down from `Integer.MAX_VALUE - 1000`). `UnsafeValues#nextEntityId` changed signature in 26.3 and is deprecated.
2. **Seat the player:** `WrapperPlayServerSetPassengers(seatId, new int[]{player.getEntityId()})`.
3. **Move the view:** `WrapperPlayServerCamera(cameraId)`.
4. **Optional, clean screen:** `WrapperPlayServerChangeGameState(Reason.CHANGE_GAME_MODE, 3f)`. Only the client goes to spectator. It hides the hotbar, hearts, hand, crosshair and XP bar (chat stays). The seat survives, and the server keeps the real game mode.

## What the client then sends

- **Rotation:** `PLAYER_ROTATION` every tick (20 a second) carrying the mouse-driven yaw/pitch. The view stays frozen, and the server's position for the player never changes. With a camera alone (no seat), the client sends no rotation at all.
- **Clicks:** in client spectator, both left and right clicks on empty space arrive as `SPECTATE_ENTITY`, indistinguishable from each other. There's no miss cooldown: 10 clicks at 5 a second all arrived. A click spent focusing the window never arrives.
- **F and Q:** arrive as `PLAYER_DIGGING` (swap hands, drop) even in client spectator. Number keys send nothing.
- **Esc:** invisible. Rotation and tick-end keep arriving through the pause screen.
- **Shift:** arrives as `PLAYER_INPUT` and doesn't unseat a client-only seat, so it works as a close key.

## A cursor on it

Text displays 2 blocks in front of the camera with billboard FIXED, facing it (yaw + 180), at full brightness. Move a dot display once per server tick by the summed mouse turn since the last tick (0.03 blocks per degree; +yaw is right, +pitch is down), using `teleport` with `setTeleportDuration(1)`. The user rated it smooth and responsive at local ping. Once |pitch| > 60, send an absolute `PlayerRotation(yaw, 0)` and ignore the next rotation (it's the echo): nothing visible happens and the cursor never sticks.

## Restore

1. `Camera(player.getEntityId())`.
2. `SetPassengers(seatId, [])`.
3. `DestroyEntities(seat, camera)`.
4. Re-send the real game mode (0 survival, 1 creative, 2 adventure, 3 spectator).
5. `player.teleport(player.getLocation())` to resync.

This gave a clean HUD and no "moved wrongly". The head keeps the rotation the mouse gave it, so save yaw/pitch before freezing and restore them afterwards.

## Pitfalls

- **Death:** a frozen player can't defend themselves. In testing one was killed by a mob, and the respawn silently reset the client, dropping the seat and camera. Make the player safe or close the menu on damage and death, and clear per-player state on respawn.
- **Seated overlay:** the game shows "Press Left Shift to dismount" while seated, so cover it with your own action bar text.
- **Quit:** after a quit, client-only state is gone, but real per-player entities you spawned stay in the world. Remove them on quit, or use client-only entities for the panel too.
- **Not proven:** latency at real ping, and Bedrock.
