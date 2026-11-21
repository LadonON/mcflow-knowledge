---
title: "Create's processing machines on a vanilla Paper 26.3 server"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "MachineServiceTest (millstone, press on depot, mixer brass, deployer assembly step, drill, crushing wheels, burner light) and MachineRulesTest in plugins/createpaper; in game 2026-11-21 at x 400-432, y 120, z 400-405, 16 RPM creative motors: millstone 3 wheat -> 3 wheat flour; press over depot 2 iron ingots -> 2 iron sheets; mixer over a coal-fed burner and basin copper + zinc -> 2 brass ingots; fan blowing through water magma block -> obsidian; drill broke stone (cobblestone dropped); saw felled a 5-log column (5 oak logs dropped); deployer holding a cogwheel turned a golden sheet on its depot into incomplete_precision_mechanism, step 1, damage 93/100; crafters 1 x 2 with oak planks -> 4 sticks; crushing wheels 1 cobblestone -> 1 gravel below the gap (server/screenshots/processing-machines/)"
sources:
  - "Create 6.0.11 (MIT): kinetics/millstone/MillstoneBlockEntity, crusher/CrushingWheelBlock and CrushingWheelControllerBlockEntity, press/PressingBehaviour and MechanicalPressBlockEntity, mixer/MechanicalMixerBlockEntity, saw/SawBlockEntity and TreeCutter, fan/AirCurrent and processing/FanProcessing, base/BlockBreakingKineticBlockEntity, deployer/DeployerBlockEntity, crafter/MechanicalCrafterBlockEntity, logistics/depot/DepotBehaviour, AllBlocks (setImpact)"
  - "research/Plugin-driven Block Breaking on Paper 26.3.md, research/Encased Fan Air Current on Paper 26.3.md, research/Deployer Fake Player Actions on Paper 26.3.md"
date: 2026-11-21
---

# Create's processing machines on a vanilla Paper 26.3 server

Implemented in `createpaper.machine` (`MachineService` ticks, saves and loads; one class per machine).

## Kinetics

Stress impact per RPM (AllBlocks `setImpact`): millstone 4, crushing wheel 8, press 8, mixer 4, saw 4, fan 2, drill 4, deployer 4, crafter 2. Shafts:

- millstone: a small cog standing up, shaft at the bottom only; mixer: the same with the shaft at the top;
- fan, drill, sideways saw: one shaft end at the back;
- deployer, saw facing up or down: shafts both ends along `DirectionalAxisKineticBlock#getRotationAxis(facing, AXIS_ALONG_FIRST_COORDINATE)`;
- press, crushing wheel: an ordinary shaft along their axis;
- crafter: a small cog on its facing axis with no shaft. It turns by meshing with a cog or another crafter beside it.

## Ticking

Every machine ticks only while it turns or has work in hand (`Machine#busy`), with a per-tick budget (`machines.max-ticks-per-tick`) taken round robin. Measured 2026-11-21: 320 running fans added 1.8 ms to an idle server, and 50 wandering bots with the full factory field were 4.3% over the kinetics baseline (31.9 ms median against 30.6).

## Rules that matter

- **Crushing wheels** throw their output out of the gap, and the output's box still overlaps the gap. Without Create's `BypassCrushingWheel` tag the wheels take it straight back in for ever (cobblestone became gravel, then sand). Tag ejected items in their PDC with the gap's position and skip them on intake. Valid only while the two wheels turn opposite ways; the side items leave is `axis × side`, signed by this wheel's speed.
- **Press**: work starts when the head is down, at half of the 240-unit cycle. The cycle moves `pressRunningSpeed` units a tick. A basin two blocks down takes compacting; a depot two down takes one item at a time; otherwise items on the ground in the block below get pressed. A single held item on a depot turns into the result in place, so assembly steps can follow.
- **Basins** also run the server's own crafting recipes: shaped 2×2 or 3×3 with one ingredient in the press, shapeless with two or more ingredients in the mixer (Create's allowShapedSquareInPress and allowShapelessInMixer). They're read from `Bukkit#recipeIterator` at start-up, after our own are registered.
- **Fan**: Create discards an item whose washing rolls no output (FanProcessing line 43). Gravel vanishing 65% of the time is correct. Use a 100% recipe (magma block -> obsidian) to test.
- **Blocks broken by machines**: `Block#breakNaturally(null, true, false)` drops what a tool-less break drops and shows the effect. It fires no event, so the drill, saw and deployer first fire `createpaper.block.ProtectionCheck` events as the machine's owner. Our own listeners ignore those. Machines placed without a player skip the check; with the owner offline, `machines.protection.offline-owner-allowed` decides.
- **Break progress** shows through `Player#sendBlockDamage(location, progress, id)` with a negative id derived from the machine's position, sent to players within 32 blocks.
- **Moving parts** (press head, mixer head and pole, deployer arm and the held item) are display translations with interpolation (`BlockVisuals#setSlide`): one metadata packet per part per viewer at each start or end of a movement. Not saved: a reloaded machine shows its parts at rest.
- **Saw blades** are a texture animation in Create, not a turning model. The blade model (active, reversed or inactive) is redrawn when the speed's sign changes. After redrawing, reapply the turning parts (`KineticService#redrawMotion`), since a new model starts still.

## Not proven yet

Fan smoking, blasting and haunting, and fans pulling. The saw cutting items on top, including stonecutting. Mixing with the server's shapeless recipes. The press compacting in a basin, and pressing ground items in game. Mechanical crafting on a 5×5 grid in game. The deployer's bone meal, block placing and item application. Protection checks with a real protection plugin.
