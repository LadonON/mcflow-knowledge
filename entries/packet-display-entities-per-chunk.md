---
title: "Per-chunk client-only ItemDisplay block models with PacketEvents on Paper 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/kinetic-network/motor-minus-64-a.png and -b.png (spinning from network speed), server/screenshots/block-framework/casing-and-shafts-xyz.png, after-restart-loaded.png, fill-4000-blocks.png; gate_performance 2026-11-17 12:10 (1,995 displays, 50 wandering bots: median 23.3 ms, p95 30.2 ms, 0 kicks); gate_memory pass; gate_performance 2026-11-17 13:52 with spin budget (1,922 spinning shafts, 50 bots: 0 kicks, median 22.5 ms, p95 42.2 ms); server/screenshots/rotation-spike/packet-9-shafts-32rpm-*.png; item-display turn: server/screenshots/kinetics-batch/furnace-block-vs-item-display.png (2026-11-18), wall gauge and cranks before and after the fix: lineup-top-down.png, fixed-lineup-top-down.png, fixed-wall-gauge-and-cranks.png"
sources:
  - "packetevents-api 2.14.0 jar (javap): WrapperPlayServerSpawnEntity, WrapperPlayServerEntityMetadata, EntityDataTypes, User.writePacket/flushPackets"
  - "packetevents-spigot 2.14.0 jar (javap -c): SpigotReflectionUtil.generateEntityId uses the server's Entity counter"
  - "paper-api 26.3.build.253-stable: io.papermc.paper.event.packet.PlayerChunkLoadEvent/PlayerChunkUnloadEvent, Chunk#getPlayersSeeingChunk"
date: 2026-11-18
---

# Per-chunk client-only ItemDisplay block models with PacketEvents on Paper 26.3

A block model can be shown with a fake `ItemDisplay` entity that exists only on clients: no server entity, no ticking, nothing saved.

## Which players get it

Follow the chunks each client has, using Paper's events (both fire on the main thread):

- `PlayerChunkLoadEvent`: send spawn and metadata for every model in that chunk.
- `PlayerChunkUnloadEvent`: send one `DestroyEntities` with all their ids.
- A block placed or removed later: send to `chunk.getPlayersSeeingChunk()`.

With that, no per-player state is needed. `gate_memory` showed no growth across join/leave cycles.

## Packets (26.3 indices)

- `new WrapperPlayServerSpawnEntity(id, UUID.randomUUID(), EntityTypes.ITEM_DISPLAY, new Location(x + .5, y + .5, z + .5, 0, 0), 0f, 0, new Vector3d())`
- Metadata: 23 = item (`EntityDataTypes.ITEMSTACK`), 17 = view range (`FLOAT`, 1.0 = 64 blocks), 13 = left rotation (`QUATERNION`), 14 = right rotation, 8/9 = interpolation start/duration (`INT`).
- Item: any vanilla item with `DataComponentTypes.ITEM_MODEL` set to your item definition, converted with `SpigotConversionUtil.fromBukkitItemStack`. The default display context draws the model 1 block tall, centred on the entity.
- Entity ids: `SpigotReflectionUtil.generateEntityId()` increments the server's own entity counter, so it can't collide with real entities.
- Batch with `user.writePacket(...)`, then one `user.flushPackets()`.
- `getUser(player)` can return null (before injection, after quit).

## Orientation

Draw models along Y and turn them with the left rotation: X axis = 90° around Z `(0, 0, √½, √½)`, Z axis = 90° around X `(√½, 0, 0, √½)`. Proven in game for all three axes. Spinning goes in the right rotation, so it applies before the axis turn; proven in game with X-axis shafts and cogs spinning.

- **Item displays turn the model 180° about Y.** A vanilla furnace placed facing north shows its front to the north. The same furnace as an `item_display` with no rotation shows its back to the north. So a display oriented with a blockstate's x/y rotation faces the opposite way, unless a 180° Y turn is added innermost: right rotation = (spin or needle turn) × rotY(180). Keep it out of any pivot maths, which works in model space (`PacketBlockVisuals#ITEM_DISPLAY_TURN`). Symmetric models (shafts, casings) hide the turn. It showed on wall gauges (dial on the wrong side), cranks, and the clutch's stopped half.

## Cost

- **Static models:** 1,995 displays seen by 50 bots added no measurable tick time.
- **Spinning from kinetic speed:** send indices 8 = 0, 9 = step ticks and 14 = right rotation around Y each time the previous step ends. A packet that arrives early adds the rest of the old step to the new turn, so keep the step plus one more tick's turn under 180°. `RotationStep` caps steps at 120° and 60 ticks. Proven in game with shafts and cogs at 16 and 64 RPM.
- **Spin budget per player (needed):** without one, 1,922 shafts spinning at 16 RPM are about 1,540 metadata packets/s for every player near them, and 17 of 50 mineflayer bots dropped (10 bots: none). One bot process takes about 15k packets/s in total, not about 77k. `SpinBudget` plus `PacketBlockVisuals.refreshBudgets` give each player updates only for the nearest spinning chunks within `visuals.spin-range` (48), up to `visuals.spin-budget` (300) packets/s. Refresh once a second; the per-player map is rebuilt from online players each time, so it can't leak. Farther models pause at their last angle.
- **Snap before resuming:** when a chunk enters a player's budget, first send the current angle with interpolation duration 0. Otherwise the gap between the client's stale angle and the new target can be over 180° and the model spins the wrong way to catch up.
- **Measured with the budget:** the same 1,922 spinning shafts with 50 wandering bots gave 0 kicks; median 22.5 ms, p95 42.2 ms (baseline 28.6 / 52.8). Memory and thread-safety gates pass. Real-client frame rate isn't measured yet.
