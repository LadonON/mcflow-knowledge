---
title: "Create's rotation and stress rules, as a whole-network solver"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "KineticSolverTest (15), TransmissionTest (9) and KineticServiceTest (7) in plugins/createpaper; in game: /createpaper inspect on motor -> 3 shafts -> cog -> meshing cog -> large cog gave 16, -16, 8 RPM and -64, 64, -32 after /createpaper speed -64 (server/screenshots/kinetic-network/); on the server 2026-11-18: motor into a gearbox gave -16 / +16 / -16 on the east / south / north shafts, a redstone block stopped the shaft past a clutch (0 RPM, network of 1) and reversed the one past a gearshift (-16), a hand crank used by a bot gave 32 RPM and 256 su then 0 after 10 ticks, and flowing water over a water wheel gave 8 RPM and 256 su; all survived a restart"
sources:
  - "Create 6.0.11 (MIT): content/kinetics/RotationPropagator.java, KineticNetwork.java, base/KineticBlockEntity.java#convertToDirection, motor/CreativeMotorBlockEntity.java"
  - "Create 6.0.11 AllBlocks.java CStress values; infrastructure/config/CKinetics.java maxRotationSpeed"
  - "Create 6.0.11: transmission/GearboxBlockEntity, SplitShaftBlockEntity, ClutchBlockEntity, GearshiftBlockEntity, chainDrive/ChainDriveBlock, crank/HandCrankBlockEntity, waterwheel/WaterWheelBlockEntity, gauge/SpeedGaugeBlockEntity and StressGaugeBlockEntity"
date: 2026-11-18
---

# Create's rotation and stress rules, as a whole-network solver

Implemented in `createpaper.kinetics` (`Connections`, `KineticSolver`, `KineticService`).

## Connection ratios (from RotationPropagator)

- **Shaft end to shaft end:** both blocks have a shaft towards each other: ×1. Shafts, cogs and large cogs have both ends along their axis; a creative motor has one, towards its facing.
- **Small cog ↔ small cog:** side by side (not along their shared axis): ×-1.
- **Large cog → small cog:** same axis, diagonal in the plane they share (offset ±1 on both other axes): ×-2. Small → large: ×-0.5.
- **Large cog ↔ large cog:** different axes, offset non-zero on exactly those two axes: sign = `(diff[fromAxis] > 0) XOR (diff[toAxis] > 0) ? -1 : 1`.
- Same-axis large cogs side by side don't mesh.

The candidates are the 6 face neighbours plus the 12 edge diagonals.

## Transmissions (each half of a block gets a face factor)

Shaft-end ratio = factor(from's face) / factor(to's face); a factor of 0 means no shaft on that face.

- **Gearbox** (axis A, shafts on the 4 faces off A): with `first = (A == X ? Y : X)`, a face on the first axis has factor 1 if it points positive, else -1; faces on the remaining axis are the other way round. A motor into the west face of a Y gearbox gives east -1, south +1, north -1.
- **Clutch / gearshift** (both ends along A): the negative-side half is 1. The positive-side half is 1 unpowered; powered it's 0 (clutch: disconnected) or -1 (gearshift: reversed).
- **Encased chain drive:** two side by side on the same axis (neighbour off the axis) turn together (×1). Create's start/middle/end chain shapes aren't modelled.
- **Hand crank:** a source with its shaft at `facing.opposite`. Each use keeps it turning 10 ticks at 32 RPM (sneaking: backwards); capacity 8 su per RPM.
- **Water wheel:** shafts at both ends. Flow score = sum over the 4 neighbours in its plane of `dot(rotate90(flow), offset) > 0.5 ? ±1`, using `FluidData.computeFlowDirection` and a right-handed 90° rotation about the axis; speed = clamp(score) × 8, capacity 32. Re-checked every 60 ticks, as Create's lazy tick does.
- **Gauges** pass rotation along their shaft. Speedometer dial uses Create's tiers (30 medium, 100 fast, 256 max); stressometer dial = stress / capacity, 1.125 when overstressed.

## Re-solving after a change that can split a network

When a change can cut a network in two (breaking a block, a chunk unloading, a clutch engaging), re-solve from every member of the old network, not only from the changed block. Solving only from the clutch left the cut-off shaft at its old 16 RPM (found on the server, fixed in `KineticService#checkPower`, pinned by `engagingAClutchStopsTheFarSide`).

## Testing from the console

With no players online, a chunk that `/createpaper place` loads over RCON unloads again straight away (seen at chunk 2,0 on the 26.3 test server), so `/createpaper inspect` says there's no Create block there. Run `/forceload add` over the test area first.

## Sources and conflicts

- A motor's setting is relative to its facing: Create's `convertToDirection` negates it when the facing points in a negative direction (west, down, north). Two motors facing each other at the same setting therefore **oppose** each other.
- The fastest source sets the speed (Create's "overpowering"). Sources that want opposite directions conflict. Anything over 256 RPM (`maxRotationSpeed`) conflicts. A gear loop whose ratios disagree conflicts. As in Create, the block that caused the conflict breaks.

## Stress (from KineticNetwork)

Capacity = Σ source capacity × |generated RPM|. Stress = Σ impact × |RPM|. The network runs while stress ≤ capacity; an overstressed network stops. Defaults: the creative motor has 16,384 su per RPM and 16 RPM by default (-256..256); shafts and cogs have impact 0; the hand crank has capacity 8 at 32 RPM.

## Design notes

- The whole connected network is re-solved on every change instead of Create's incremental source pointers. Changes are rare (place, break, setting, chunk load or unload), so nothing runs per tick.
- Not done yet: Create remembers an unloaded part's stress and capacity. Here a network cut by an unloaded chunk runs on its loaded part only.
- Not done yet: cog teeth phase alignment.
- Redstone power is read from `Block#isBlockIndirectlyPowered` on `BlockPhysicsEvent` for our barrier stand-ins; a `/setblock` next to the block fires it.
