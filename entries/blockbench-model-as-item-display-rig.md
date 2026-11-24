---
title: "Blockbench bone models as an ItemDisplay rig on 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/phase2-model/preview-t1.png, preview-end-lock-back.png; server/screenshots/phase2-opening/t04.png; LegendaryCrateModelTest (6 tests); gate_resource_pack pass on resourcepacks/superiorcrates (2026-11-24)"
sources:
  - "research/Bone Models as Item Models in 26.3.md (client jar javap)"
  - "research/Blockbench bbmodel Format.md"
  - "https://minecraft.wiki/w/Model"
date: 2026-11-24
---

# Blockbench bone models as an ItemDisplay rig on 26.3

Proven with a Blockbench 5 Generic Model (`model_format: free`, format 5.0): three bones, 31 cubes, two embedded textures and a 4.5 s animation. The model renders the right way round, at its Blockbench size, and animates smoothly.

## Pack (pack format 97.1)

- **pack.mcmeta:** `{"pack":{"description":"…","min_format":[97,1],"max_format":97}}` loads in the 26.3 client and passes `gate_resource_pack`.
- **One model per bone:** `assets/<ns>/models/<model>/<bone>.json`, plus `assets/<ns>/items/<model>/<bone>.json` containing `{"model":{"type":"minecraft:model","model":"<ns>:<model>/<bone>"}}`. The display's item is any material (paper) with `ItemMeta#setItemModel("<ns>:<model>/<bone>")`.
- **Textures:** in `assets/<ns>/textures/item/<model>/<n>.png`, referenced as `<ns>:item/<model>/<n>`, which the items atlas picks up.
- **Element coordinates:** written relative to the bone pivot, with the pivot at (8, 8, 8): `c' = 8 + (c − pivot) / k`. Choose k ≥ 1 so every corner fits inside [−16, 32]. That's ±24 from the pivot, padded by √3 if any cube is rotated.
- **UVs:** convert from texture pixels to the 0..16 space: `u · 16 / uv_width`, `v · 16 / uv_height`. Mirrored UVs (u1 > u2) work as is.
- **Cube rotations:** write Euler `{"origin":…, "x":…, "y":…, "z":…}` straight from Blockbench. A single-axis ±45° on Y matches Blockbench in game. Multi-axis cubes are still unproven.

## Display placement

- **Spawn:** one `ItemDisplay` per bone that has cubes, all at the rig origin, with `ItemDisplayTransform.NONE`, `setPersistent(false)`, and billboard FIXED.
- **Transform:** NONE puts the item's (8, 8, 8) at the entity and ignores the model's `display` block. The renderer also turns the item 180° about Y. So the display transform is `base · FLIP · global · T(pivot) · S(k) · FLIP`, where FLIP = rotationY(π), `global` is the bone's posed matrix in blocks, and `base` is the rig's facing and scale. With `base = rotationY(π − yaw)`, the model's front (Blockbench −Z, where the lock is) faces a player looking along `yaw`.
- **Animation:** send poses every 2 ticks with `setInterpolationDelay(0)`, `setInterpolationDuration(2)`, then `setTransformationMatrix`. Motion looks smooth.

## Bone poses (Blockbench 5 semantics)

- **Local transform:** `T(position/16) · T(pivot) · R · S(scale) · T(−pivot)`, where R = `rotateZYX(z, y, x)` of rest rotation plus keyframe rotation, in radians. Global = parent global · local. The outliner lists parents before children.
- **Signs:** format 5.0 values are used as is. A positive X rotation on a lid hinged at its back lifts the front, which matches Blockbench.
- **Keyframes:** they're saved unsorted, so sort by time. Catmull-rom applies to a segment if either end asks for it, using neighbour keyframes (or the ends) as control points.
- **Unknown bones:** animators keyed to a bone UUID that isn't in the model (e.g. a `vfx` locator) must be skipped.

## Not yet proven

- Cubes rotated on more than one axis.
- Bones whose shrink factor k is above 1.
- Mesh elements.
- Bezier keyframes (treated as linear).
- Files older than format 5.0 (refused; they store some signs flipped).
