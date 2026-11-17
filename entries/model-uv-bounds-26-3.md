---
title: "26.3 client refuses block/item models with UVs outside 0..16"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "26.3 client log (logs/latest.log) 2026-11-17 12:42:19: 'Unable to bake item model: create:creative_motor ... Cannot compute translucency out of bounds: [14, 4, 20, 10] in 16x16 image'; after clamping, server/screenshots/kinetic-network/motor-fixed-a.png"
sources:
  - "26.3 client stack: NativeImage.computeTransparency <- SpriteContents.computeTransparency <- FaceBakery.computeMaterialTransparency <- FaceBakery.bakeQuad"
date: 2026-11-17
---

# 26.3 client refuses block/item models with UVs outside 0..16

On 26.3, the client works out each face's transparency from the texture area its UV covers. If a face's `uv` goes past the texture (any value below 0 or above 16), it throws `IllegalArgumentException: Cannot compute translucency out of bounds` and the **whole model** fails to bake. You then get the magenta-and-black missing-model cube. Older versions wrapped such UVs, so models made for 1.21 and earlier can carry them.

`gate_resource_pack` does **not** catch this: it passed the broken pack. Check the client log (`Unable to bake item model`) or scan for it.

## Fix

Clamp every face UV to 0..16. That squeezes those faces a little, but the model loads. `tools/pack-gen/fix_uv_bounds.py <pack> <overlay>` finds the affected models and writes clamped copies into an overlay pack.

In Create 6.0.11 there are 5 affected models: `block/creative_motor/{block,block_vertical,item}`, `block/goggles` and `item/extendo_grip/item`.
