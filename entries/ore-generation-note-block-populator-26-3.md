---
title: "Custom ore generation with a BlockPopulator and note-block states on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "ZincOrePopulatorTest and SurvivalObtainabilityTest (generatedOreIsAdoptedWhenFirstTouched, miningZincOreWithAnIronPickaxeDropsRawZinc, aPlayerPlacedNoteBlockIsNeverTakenForOre) in plugins/createpaper; RCON counts on Paper 26.3-253 2026-11-19 (16 fresh chunks: 239 zinc ore, 650 deepslate zinc ore; another 16: 738 and 491, spread evenly from y -64 to 63); server/screenshots/survival-obtainability/zinc-veins-xray.png, deepslate-zinc-vein-close.png"
sources:
  - "paper-26.3.jar: net.minecraft.world.level.chunk.ChunkGenerator.applyBiomeDecoration, org.bukkit.craftbukkit.generator.CraftLimitedRegion (javap)"
  - "paper-api-26.3.build.253-stable.jar: org.bukkit.generator.BlockPopulator, LimitedRegion, WorldInitEvent"
  - "Create 6.0.11 (MIT): worldgen/configured_feature/zinc_ore.json, worldgen/placed_feature/zinc_ore.json, AllBlocks.ZINC_ORE"
date: 2026-11-19
---

# Custom ore generation with a BlockPopulator and note-block states on Paper 26.3

Implemented in `createpaper.worldgen.ZincOrePopulator` and `BlockService#lookup`. Background: `research/Ore Generation with Block Populators on Paper 26.3.md`.

## Generation

- Add the populator to `World.getPopulators()` for every loaded world in `onEnable`, and in `WorldInitEvent` for later ones. Paper runs it after vanilla decoration for every newly generated chunk, vanilla generator included. Chunks generated before that never get it.
- It runs on chunk-generation threads. Touch only the `LimitedRegion`, `WorldInfo` and your own final fields. Build the target material sets (`Tag.STONE_ORE_REPLACEABLES`, `Tag.DEEPSLATE_ORE_REPLACEABLES`) and the note-block `BlockData` on the main thread first.
- Paper hands every populator of a chunk the same decoration-seeded `Random`. Mix a salt into a fresh `Random` of your own.
- Check `region.isInRegion(x, y, z)` before each `getType`/`setBlockData`. Veins that start inside the chunk and reach 3 to 4 blocks out stay in the region.
- Create's zinc numbers (8 veins per chunk, size 12, y -63 to 70, stone → zinc ore, deepslate/tuff → deepslate zinc ore) gave 55 to 77 ore blocks per chunk. The split between stone and deepslate depends on the terrain.
- Cost: 144 fresh chunks took 4.5 to 6.5 s with the populator warm and 5.4 to 5.8 s without, so the difference is below the noise at this sample size. It's not proven to be free.

## The ore can't be in the block store at generation time

Generation can't write the chunk PDC, where placed note-block blocks are recorded. So a block definition marked `generated` is **adopted** the first time anything looks at it: an untracked note block whose state is a generated block's state gets a store entry on lookup (`isOurs`, `definitionAt`, `destroy`).

- The check that pins player-placed note blocks to state 0 must use the store only (`isTracked`). Otherwise a fresh vanilla note block in the ore's state would be adopted as ore.
- Give generated blocks states vanilla note blocks never take on their own. Here: `custom_head` instrument (needs a player head on top) with notes 23 and 24 (needs tuning).
- Note-block updates must stay off (`block-updates.disable-noteblock-updates: true`, see `note-block-custom-blocks-26-3.md`), or neighbours change the ore's state before it's adopted.

## Drops

Create's ore loot: raw zinc, Fortune with vanilla's ore bonus (`max(nextInt(L + 2) - 1, 0) + 1` times), Silk Touch gives the ore, and `needs_iron_tool`. That's `Harvesting` with `needs_tool` and `drops` in blocks.json. Tested with MockBukkit break events.

## Not proven

- Mining by a real player in survival. The bots can't hold left-click, so only unit tests cover the break path. Break speed is still the vanilla note block's (axe, hardness 0.8), not gold ore's.
