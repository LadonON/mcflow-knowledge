---
title: "Create's rotation and stress rules, as a whole-network solver"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "KineticSolverTest (15 tests) and KineticServiceTest (6 tests) in plugins/createpaper; in game: /createpaper inspect on motor -> 3 shafts -> cog -> meshing cog -> large cog gave 16, -16, 8 RPM and -64, 64, -32 after /createpaper speed -64 (server/screenshots/kinetic-network/)"
sources:
  - "Create 6.0.11 (MIT): content/kinetics/RotationPropagator.java, KineticNetwork.java, base/KineticBlockEntity.java#convertToDirection, motor/CreativeMotorBlockEntity.java"
  - "Create 6.0.11 AllBlocks.java CStress values; infrastructure/config/CKinetics.java maxRotationSpeed"
date: 2026-11-17
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

## Sources and conflicts

- A motor's setting is relative to its facing: Create's `convertToDirection` negates it when the facing points in a negative direction (west, down, north). Two motors facing each other at the same setting therefore **oppose** each other.
- The fastest source sets the speed (Create's "overpowering"). Sources that want opposite directions conflict. Anything over 256 RPM (`maxRotationSpeed`) conflicts. A gear loop whose ratios disagree conflicts. As in Create, the block that caused the conflict breaks.

## Stress (from KineticNetwork)

Capacity = Σ source capacity × |generated RPM|. Stress = Σ impact × |RPM|. The network runs while stress ≤ capacity; an overstressed network stops. Defaults: the creative motor has 16,384 su per RPM and 16 RPM by default (-256..256); shafts and cogs have impact 0; the hand crank has capacity 8 at 32 RPM.

## Design notes

- The whole connected network is re-solved on every change instead of Create's incremental source pointers. Changes are rare (place, break, setting, chunk load or unload), so nothing runs per tick.
- Not done yet: Create remembers an unloaded part's stress and capacity. Here a network cut by an unloaded chunk runs on its loaded part only.
- Not done yet: cog teeth phase alignment.
