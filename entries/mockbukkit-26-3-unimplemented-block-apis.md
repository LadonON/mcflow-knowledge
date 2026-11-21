---
title: "Block and item APIs MockBukkit for 26.3 doesn't implement"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "gradlew test in plugins/createpaper on 2026-11-21: MachineServiceTest cases were reported as skipped with UnimplementedOperationException until these calls went through MachineService.WorldFacts"
sources:
  - "Stack traces from the test reports: org.mockbukkit.mockbukkit.block.BlockMock and inventory.ItemTypeMock"
date: 2026-11-21
---

# Block and item APIs MockBukkit for 26.3 doesn't implement

MockBukkit throws `UnimplementedOperationException` for these. JUnit then reports the test as **skipped**, not failed, so a green run can hide it: read the skipped count.

- `Block#getBlockSoundGroup` (BlockMock:447)
- `Block#isBlockPowered` (BlockMock:351), and `isBlockIndirectlyPowered`
- `Block#isPassable` (BlockMock:601)
- `Material#getCraftingRemainingItem` (ItemTypeMock:261)

Route them through a small interface the tests swap, as the project already does for fuels and surroundings (`MachineService.WorldFacts`, `ProcessingService.Fuels`, `KineticService.Surroundings`).

These work under MockBukkit: `World#getNearbyEntities(BoundingBox, Predicate)`, `World#dropItem`, item-entity PDC, `Block#breakNaturally(ItemStack, boolean, boolean)` and `getRecipeIterator`. `Bukkit#craftItemResult` wasn't tried; the mechanical crafter was proven in game instead.
