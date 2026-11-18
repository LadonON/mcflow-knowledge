---
title: "Create's blaze burner and basin on a vanilla Paper 26.3 server"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "BlazeBurnerTest (7), BasinContentsTest (6), ProcessingServiceTest (12), ProcessingSpeedTest (5) in plugins/createpaper; on the server 2026-11-18: a bot fed one coal to a burner (3 -> 2 coal), /createpaper inspect gave 'kindled, normal fuel, 1008 ticks left' after a server restart; wheat and sugar summoned above a basin went in (12 wheat 3 sugar) and showed in its bowl; the burner under the basin drew Create's active blaze head (server/screenshots/kinetics-processing-leftovers/burner-basin-valve.png, basin-from-above.png)"
sources:
  - "Create 6.0.11 (MIT): content/processing/burner/BlazeBurnerBlockEntity.java (tick, tryUpdateFuel, getHeatLevel, applyCreativeFuel), BlazeBurnerBlock.java (tryInsert, HeatLevel), BlazeBurnerBlockItem.java (capturing a blaze), BlazeBurnerRenderer.java (getBlazeModel, headY)"
  - "Create 6.0.11: content/processing/basin/BasinBlockEntity.java, BasinInventory.java, BasinBlock.java (useItemOn, updateEntityAfterFallOn), data/create/data_maps/item/superheated_blaze_burner_fuels.json, data/create/tags/block/passive_boiler_heaters.json"
  - "paper-api 26.3.build.253: ItemType#getBurnDuration, Material#getCraftingRemainingItem, ItemStack#serializeAsBytes"
date: 2026-11-18
---

# Create's blaze burner and basin on a vanilla Paper 26.3 server

Implemented in `createpaper.processing` (BlazeBurner, BasinContents, BasinStore, ProcessingService, ProcessingListener).

## Burner fuel (BlazeBurnerBlockEntity)

- Heat capacity 10,000 ticks; a fuel of the same kind only tops up below 500 ticks left, except a player's normal fuel, which overflows up to 10,000 (and is used up even when full). Better fuel replaces worse; worse is refused.
- Normal fuel: anything a furnace burns, for its furnace burn time (`ItemType#getBurnDuration`: coal 1,600, a lava bucket 20,000 and it leaves its bucket). An empty burner takes a lava bucket's 20,000 whole, above the capacity.
- Superheating: Blaze Cake, 3,200 ticks (the data map); when it runs out the burner drops to normal fuel with 5,000 ticks.
- Heat: superheated → SEETHING; normal → KINDLED, FADING below 1.25 % of capacity (under 125 ticks); none → SMOULDERING. A Creative Blaze Cake fixes the heat for good, one active level up each time, skipping FADING.
- Create's fuel tags `blaze_burner_fuel/regular` and `/special` are empty in 6.0.11; only the data map and furnace fuels count.
- An empty blaze burner catches a blaze from a blaze or a blaze spawner (which stays) and becomes a blaze burner item.

## Heat a basin gets (BasinBlockEntity#getHeatLevelOf)

A blaze burner below gives its level. Magma, lava, fire, soul fire and lit campfires (`passive_boiler_heaters`) give SMOULDERING. Anything else, an empty burner included, gives NONE.

## Basin

- 9 input and 9 output slots, up to 99 items each (unstackable ones too), each kind of item in one slot only, the first empty slot taken. Outputs go in whole or not at all.
- Two input and two output tanks of 1,000 mB, saved but not filled by anything yet.
- An empty hand takes everything out; breaking the basin drops it all.
- Items in: Create takes item entities that fall into its bowl. Our barrier stand-in is a full cube, so items rest on top; every 4 ticks each loaded basin takes the items in the box `y + 1 … y + 1.25` above it.
- Contents are saved in the chunk PDC as one byte array per basin (`ItemStack#serializeAsBytes`, which Paper upgrades across versions), written on chunk unload and world save.

## Server and display notes

- Burner state lives in memory while loaded and goes into the block's value (heat bits 0-2, fuel 3-4, creative 5, working-under-a-basin 6, burn time from bit 7) when its heat changes, on chunk unload and on world save, so only burners with fuel tick and the store isn't written every tick.
- The working blaze head (KINDLED or hotter with a basin above; Create's `blaze/active` and `blaze/super_active`) sinks 0.75 blocks, as BlazeBurnerRenderer's `headY` does.
- The burner's cage is an OBJ model in Create, so it's a placeholder of our own for now; the heads and the basin are Create's JSON models.
- MockBukkit implements neither `ItemType#getBurnDuration` nor `getCraftingRemainingItem`, and a test that calls them is reported as skipped. The fuel facts go through a swappable `ProcessingService.Fuels`.

## Not done yet

The lit blaze burner (flint and steel on an empty one), goggles on the blaze, light from the burner, a basin's output to the side, and fluids in and out.
