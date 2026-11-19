---
title: "Converting Create's OBJ models to Java block models for 26.3 display entities"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/converted-obj-models/flywheel.png, large-water-wheel.png, large-water-wheel-with-rim.png, valve-and-burner-cage.png, water-wheel.png (2026-11-19); gate_resource_pack pass on createpaper-served; no model errors for createpaper: models in the client log (ModrinthApp profile Dev)"
sources:
  - "Create 6.0.11 (MIT) OBJ meshes and wrapper JSON models, exported by tools/asset-converter/export_obj_models.py"
  - "research/Model Element Rotation on 26.3.md (26.3 client jar: CuboidModelElement deserializer)"
  - "techno-rope.com OBJ2MC Addon Studio, its app bundle read statically with REA on 2026-11-19 (evidence ev_6b2903ae61f6649e93984b5071ca07da3906c62215d41fc96d39f10702c78ec3)"
date: 2026-11-19
---

# Converting Create's OBJ models to Java block models for 26.3 display entities

Implemented in `tools/asset-converter/obj_to_java_model.py` (input from `export_obj_models.py`, output in `assets/create-obj-models-java/` with `report.json`).

## Why not a voxelizer

techno-rope.com's OBJ2MC voxelises a mesh and colours cubes from a few quantized colours (K-Means, median cut, wool palette), with greedy meshing, and writes Bedrock `.geo.json` (format 1.12.0) plus a generated PNG. That loses Create's textures and isn't a Java model. Statically its bundle makes no upload calls (only the module-preload `fetch` and a Cloudflare analytics beacon); that is an inference from code, not an observed run.

## The conversion that works

Create's OBJs were made in Blockbench, so most pieces are boxes:

- Split each OBJ into connected pieces by shared vertex positions (one `o` object holds many pieces).
- Merge coplanar triangle pairs that share an edge and form a convex quad back into quads first (Create's water wheels are exported as triangles only).
- A piece with 8 corners and 6 quads at right angles becomes one element: build an orthonormal frame from three edges, matching each edge to its nearest world axis so small turns stay small; from/to = centre ± half extents in that frame; rotation origin = centre.
- Any other flat quad becomes a zero-thickness element with one face. A non-rectangular one (a trapezoid on a ring) uses the average of opposite sides for its size, which closes rims well enough to look whole.
- Coordinates: OBJ units are blocks with the block at 0..1; multiply by 16. With NeoForge's `flip_v: true` (all of Create's), model v = (1 - obj v) × 16. All UVs landed inside 0..16.
- Face UVs: map the face's corners to vanilla's default per-face u/v directions (down u=x v=-z, up u=x v=z, north u=-x v=-y, south u=x v=-y, west u=z v=-y, east u=-z v=-y) and try the four face rotations to match the OBJ's UVs.
- Every element in the five models in use turned about a single world axis, written as `{"origin", "axis", "angle"}` with right-handed angles, and they render the right way round on 26.3. The Euler form was never needed and is still unproven.

## Models wider than -16..32

Elements are checked before rotation, so rotated parts poke out even when the shape seems to fit. Write the model at 1/2 size about (8, 8, 8) and draw the display part at scale 2 (display SCALE metadata, `BlockLayouts#MODEL_SCALE`); add matching gui/ground/fixed display scales so the item looks right. This fits Create's flywheel (-14..30 at full size plus rotated corners) and the 3 × 3 large water wheel (-31..47) in one model each. The public pack's placeholders for those blocks are built at the same half size so one scale serves both packs.

## Results

Flywheel 146 elements, valve handle 50, blaze burner cage 38, water wheel rim 591, large water wheel 978, all rendering with Create's textures. Element counts in the hundreds draw without trouble on one client; not yet measured under load.
