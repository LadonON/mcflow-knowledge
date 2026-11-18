---
title: "Create's rotation and stress rules, as a whole-network solver"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "KineticSolverTest (15), TransmissionTest (9) and KineticServiceTest (7) in plugins/createpaper; in game: /createpaper inspect on motor -> 3 shafts -> cog -> meshing cog -> large cog gave 16, -16, 8 RPM and -64, 64, -32 after /createpaper speed -64 (server/screenshots/kinetic-network/); on the server 2026-11-18: motor into a gearbox gave -16 / +16 / -16 on the east / south / north shafts, a redstone block stopped the shaft past a clutch (0 RPM, network of 1) and reversed the one past a gearshift (-16), a hand crank used by a bot gave 32 RPM and 256 su then 0 after 10 ticks, and flowing water over a water wheel gave 8 RPM and 256 su; all survived a restart. 2026-11-18 (second batch): TransmissionTest +8 and KineticServiceTest +18 (124 tests in all at the time, none skipped); on the server at x 300, y 120: a speed controller set to 16 then -96 turned its large cog at 16 then -96 while its input ran at 16; a chain gearshift with a redstone block on it ran its chain drive at 32 from 16; an encased cog fed from below meshed at -16 and a shaft placed above it later stayed at 0; a vertical gearbox gave -16 straight through and +16 upwards; a large water wheel beside a waterfall gave 4 RPM and 512 su; a valve handle turned by a bot gave -32 RPM, 256 su, then 0; a shaft removed with /setblock was forgotten (server/screenshots/kinetics-processing-leftovers/)"
sources:
  - "Create 6.0.11 (MIT): content/kinetics/RotationPropagator.java, KineticNetwork.java, base/KineticBlockEntity.java#convertToDirection, motor/CreativeMotorBlockEntity.java"
  - "Create 6.0.11 AllBlocks.java CStress values; infrastructure/config/CKinetics.java maxRotationSpeed"
  - "Create 6.0.11: speedController/SpeedControllerBlockEntity and RotationPropagator#getConveyedSpeed, chainDrive/ChainGearshiftBlockEntity, simpleRelays/encased/EncasedCogwheelBlock, gearbox/VerticalGearboxItem, base/HorizontalAxisKineticBlock, crank/ValveHandleBlockEntity, waterwheel/LargeWaterWheelBlock and WaterWheelBlockEntity (LARGE_OFFSETS), base/KineticBlockEntityVisual#rotationOffset"
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

- **Adjustable chain gearshift:** a chain drive whose chain runs at `1 + (signal + 1) / 16` times its shaft while powered (signal = strongest redstone around it, `Block#getBlockPower`); the chain ratio between two drives is `mod(from) / mod(to)`. Shaft ends stay ×1.
- **Encased cogwheels:** mesh exactly like small and large cogs, but have a shaft at an end of their axis only where one was given (Create's top_shaft / bottom_shaft; here, set at placement towards neighbours whose shaft meets it). A shaft placed next to it later doesn't connect (Create needs a wrench for that). Placed against a small cog, it takes that cog's axis.
- **Gearbox placement:** Create's gearbox always stands on axis Y; the separate vertical gearbox lies horizontally, across the horizontal neighbours whose shafts point at it (else across the player's view, `getHorizontalDirection().getClockWise()`). Breaking each drops itself.
- **Valve handle:** a crank that turns its default 45° per use: `ceil(45 / 9.6) + 2 = 7` ticks at 32 RPM, then a 4-tick cooldown, and only while nothing else turns it. Create stops connected sequenced blocks at exactly 45°; there's nothing sequenced yet, so here it just runs 7 ticks.
- **Large water wheel:** an axis block (not a facing one) with 8 filler blocks around its centre in the plane across the axis; placement needs all 8 free, breaking any piece breaks all and drops the wheel. Speed `clamp(score, -1, 1) × 4`, capacity 128 per RPM. Its flow score checks the 12 blocks just outside the rim: `2·d` and `2·d + d2` for the in-plane directions d, d2. A waterfall down the side of the rim scores on all three blocks there.

## Rotation speed controller

The controller turns the horizontal large cog directly above it, at right angles to it, at its own setting (target RPM, default 16), whatever its input speed; while the controller is still, the cog gets nothing. That link has no ratio, so the solver floods "groups" through fixed ratios, records controller links between groups, and fixes the scale of each group in order (Kahn's algorithm): a group's own sources first, then the setting from each controller driving it, combined by the usual overpowering and opposing-sources rules. Controllers that end up driving their own group are a GEAR_LOOP conflict. All groups share one capacity and stress, as Create's network does. Approximation: a source on the cog side doesn't drive the controller's side back.

## Unloaded chunks

Create keeps an unloaded block entity's place in its network. Here, when a chunk unloads, its members of any network that still has a loaded block are kept as frozen node snapshots (cranks and valves frozen stopped), and the loaded part is re-solved through them, so their sources, stress and capacity still count. Snapshots go when their chunk loads (the real blocks take over), and as soon as a solve finds a network with no loaded block (all of it unloaded, or cut off by a broken block). Count with `/createpaper blocks`.

## Stand-ins replaced without a break event

`/setblock` and other plugins replace a barrier without a BlockBreakEvent. The neighbour updates that follow arrive as BlockPhysicsEvent with `getSourceBlock()` = the replaced block: look that up in the store (it misses at once in chunks without Create blocks) and forget it if its stand-in no longer matches. Proven in game with `/setblock … air`.

## Cog teeth phase

Display angles follow Create's clock: `angle = ticks × degrees per tick + phase`, where the phase (KineticBlockEntityVisual#rotationOffset) is 22.5° when the two coordinates off the axis add up to an even number, else 11.25° for large cogs, else 0. Java's `-1 % 2 == -1` counts as odd, as in Create. On a speed change, parts snap (interpolation 0) to the clock angle, then step as before.

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
- Redstone power is read from `Block#isBlockIndirectlyPowered` on `BlockPhysicsEvent` for our barrier stand-ins; a `/setblock` next to the block fires it.
- MockBukkit implements neither `isBlockIndirectlyPowered`, `getBlockPower` nor `getFluidData`: a test calling them is reported as *skipped*, not failed, so a green run can hide it. KineticService reads them through a swappable `Surroundings` that tests replace.
