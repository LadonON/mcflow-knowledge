---
title: "Loading Create 6.0.11's processing recipes on a vanilla Paper 26.3 server"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "RecipeRegistryTest (8 tests) in plugins/createpaper, including every vanilla id in the converted recipes resolving with Material.matchMaterial; server log 2026-11-18 08:11:59 '355 Create processing recipes loaded' on Paper 26.3-253, after the 08:07 run had left out create:mixing/mud_by_mixing for #minecraft:convertable_to_mud"
sources:
  - "Create 6.0.11 (MIT), branch mc1.21.1/dev: src/generated/resources/data/create/recipe, data/c/tags/item, data/create/tags/item; content/processing/recipe/ProcessingOutput.java and HeatCondition.java"
  - "paper-26.3.jar data/minecraft/tags (block/convertible_to_mud.json exists; no item tag of that name)"
date: 2026-11-18
---

# Loading Create 6.0.11's processing recipes on a vanilla Paper 26.3 server

Implemented in `tools/recipe-convert/convert_recipes.py` (build time) and `createpaper.recipe` (runtime).

## What Create's data looks like

- 1,881 recipe files. 835 are Create's own types (`create:milling`, `create:crushing` and so on); the rest are vanilla types.
- 515 carry `neoforge:conditions`. Most are `neoforge:mod_loaded` for compat mods, so a server without those mods drops the recipe. A few are `neoforge:not` → `tag_empty` (an ore of a metal another mod adds).
- Item ingredients are `{"item": id}`, `{"tag": id}` or a list of those. Fluid ingredients are `{"type": "neoforge:single"|"neoforge:tag"|"neoforge:components", "amount": mB, ...}`.
- Results are `{"id", "count"?, "chance"?}`. A result with `amount` is a fluid.
- Other fields: `processing_time` (ticks, default 0), `heat_requirement` (`heated` / `superheated`) and `keep_held_item` (deploying).

## Converting for a vanilla server

- A vanilla server has no `c:` tags. Create's own tag files give its members (for example `c:ingots/brass` → `create:brass_ingot`). The vanilla members NeoForge would add (`c:ingots/iron` → `minecraft:iron_ingot`, `c:stripped_logs`, `c:glass_blocks`, ...) are in a table in the converter. `create:` tags expand from Create's files.
- Keep `#minecraft:` tags as tags and resolve them against the running server, so they follow its version.
- Expanding tags at build time also handles the `tag_empty` conditions: an ingredient left with no members drops its recipe. On a vanilla server that's the 27 crushing recipes for aluminium, lead, nickel, osmium, platinum, quicksilver, silver, tin and uranium ores.
- Result: 355 recipes of 13 types. 444 are dropped for compat mods, 27 for empty tags, 7 wait for mechanical crafting and sequenced assembly, and 2 are code-driven (item copying, toolbox dyeing).

## 26.3 differences from 1.21.1

- `minecraft:convertable_to_mud` is now `minecraft:convertible_to_mud`, and it's a **block** tag only. The converter renames it. When no item tag exists, the plugin reads the block tag of that name and keeps the members that are items.
- Every vanilla item id in the 355 recipes still exists on 26.3 (checked by a test against the 26.3 Material enum).

## Create's runtime rules (ported)

- Chance outputs: each unit of `count` is rolled on its own and kept when `random.nextFloat() <= chance`.
- Heat: HEATED is met by any blaze burner level except NONE and SMOULDERING; SUPERHEATED only by SEETHING.
- The millstone counts its timer down from `processing_time` by `clamp((int) |rpm / 16|, 1, 512)` each tick; with no matching recipe it waits 100 ticks. Not wired to a machine yet (PLAN.md 5.2).
