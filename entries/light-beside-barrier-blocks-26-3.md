---
title: "Light from barrier-based custom blocks with a neighbouring light block on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "MachineServiceTest#flintAndSteelLightsAnEmptyBurnerAndAShovelPutsItOut; in game 2026-11-21: a bot lit an empty blaze burner at 432 120 400 with flint and steel and `execute if block 432 121 400 minecraft:light[level=12]` passed; a coal-fed burner with a basin on top put its light at 408 120 399 (north side)"
sources:
  - "research/Light from Custom Blocks on Paper 26.3.md (Blocks/BarrierBlock/LightBlock read from the 26.3 server jar)"
  - "Create 6.0.11 BlazeBurnerBlock#getLight, LitBlazeBurnerBlock#getLight (MIT)"
date: 2026-11-21
---

# Light from barrier-based custom blocks on Paper 26.3

A barrier can't give off light, and a `minecraft:light` block has no collision or hitbox. So a block drawn as barrier plus display entity gets its light from a light block in a free neighbouring space (`createpaper.processing.BurnerLight`):

- Try above first, then the four sides, then below. Use only air, in a loaded chunk. Neighbours in the block's own chunk are always loaded; others need `World#isChunkLoaded`, so looking never loads a chunk.
- Set the level with `Light#setLevel` and `setBlockData(data, false)`.
- Keep in memory where each block's light is. When the block goes or goes dark, remove the light only if that spot is still `LIGHT`. If something was placed there (light blocks are replaceable), find a new spot. When the chunk loads, take over a light block already next to the block.

Create's levels: blaze burner with a blaze 8 when smouldering, 15 when hotter; lit burner 12, or 9 with a soul flame.
