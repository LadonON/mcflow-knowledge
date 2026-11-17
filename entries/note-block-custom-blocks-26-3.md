---
title: "Custom full-cube blocks from note-block states on Paper 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/block-framework/casing-and-shafts-xyz.png, after-restart-loaded.png, fill-4000-blocks.png; BlockFrameworkTest (noteStatesCoverEveryInstrumentAndRoundTrip, placesNoteBlockStandIn, vanillaNoteBlocksArePinnedToStateZero)"
sources:
  - "client jar .minecraft/versions/26.3/26.3.jar: net.minecraft.world.level.block.state.properties.NoteBlockInstrument (javap -c, instrument ids)"
  - "paper-api 26.3.build.253-stable: org.bukkit.Instrument, org.bukkit.block.data.type.NoteBlock"
  - "server/config/paper-global.yml: block-updates.disable-noteblock-updates"
date: 2026-11-17
---

# Custom full-cube blocks from note-block states on Paper 26.3

A note block has **27 instruments × 25 notes × 2 powered = 1,350 states** on 26.3. Give each custom full-cube block one state, and make the resource pack draw that state with its model.

## State numbering

`index = instrument × 50 + note × 2 + (powered ? 1 : 0)`. The order of `org.bukkit.Instrument.values()` matches the client's `NoteBlockInstrument` ids:

`harp, basedrum, snare, hat, bass, flute, bell, guitar, chime, xylophone, iron_xylophone, cow_bell, didgeridoo, bit, banjo, pling, trumpet, trumpet_exposed, trumpet_oxidized, trumpet_weathered, zombie, skeleton, creeper, dragon, wither_skeleton, piglin, custom_head`

Reserve index 0 (`harp`, note 0, unpowered) for vanilla note blocks, which leaves 1,349 states for custom blocks.

## Resource pack

Override `assets/minecraft/blockstates/note_block.json` with **every** state listed explicitly (`"instrument=harp,note=0,powered=true": {"model": "createpaper:block/andesite_casing"}`). States without a custom block point to `minecraft:block/note_block`. A full-cube model with `parent: minecraft:block/cube_all` renders correctly on a 26.3 client. Generator: `tools/pack-gen/gen_blocks.py`.

## Server side (all required)

- `config/paper-global.yml`: `block-updates.disable-noteblock-updates: true`. Without it, redstone and the block below change the instrument and powered state, and the block turns into another block. Production servers need this too.
- Set the state with `block.setBlockData(data, false)` (no physics).
- Pin vanilla note blocks: on `BlockPlaceEvent`, set any note block that isn't ours to index 0. Deny `setUseInteractedBlock` on right-clicks (tuning), unless the player is sneaking to place against it.
- Cancel `NotePlayEvent` for our blocks.
- Pistons: cancel `BlockPistonExtendEvent`/`RetractEvent` when they would move one of ours.
- Fire: cancel `BlockBurnEvent` (note blocks are flammable).
- Explosions: in `Entity/BlockExplodeEvent`, take ours out of `blockList()` and drop our own item.
- Store which block is where (here: in the chunk PDC), and check it on chunk load: drop entries whose stand-in no longer has the expected state.

## Pitfall hit

If you fire `BlockPlaceEvent` yourself before recording the block, your own "pin vanilla note blocks" listener resets it to state 0. Record the block first, and roll back if the event is cancelled.

## Not proven yet

- Break speed is vanilla note block speed, whatever hardness the custom block has.
- Break and place sounds are the note block's own wood sounds on the client.
- Light, and whether a cutout or translucent texture renders on a note-block model (glass).
