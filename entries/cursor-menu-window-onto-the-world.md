---
title: "A window onto the world in a cursor menu: preview copy, projection and a pitched camera view on 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/parts-editor/front-view-fixed.png (verifier-visual PASS), top-view.png and reverify-top.png (top view at pitch 62, X/Y/Z labels on the projected arrow tips), 2026-11-27; gate_performance parts-editor (10 opped bots, 139 opens/min, median 10.6 ms vs 8.9 ms idle), gate_memory (7 cycles, no leaks) and an entity count after the runs (44 block displays = 1 placed + 43 in the one open preview), 2026-11-27"
sources:
  - "research/Moving a Client-Only Spectator Camera on 26.3.md (26.3 client jar: Camera.alignWithEntity, DisplayRenderer.calculateOrientation, LevelRenderer)"
  - "research/Per-Player Preview Copies with Glow on 26.3.md (paper-api-26.3.build.261-stable.jar)"
date: 2026-11-27
---

# A window onto the world in a cursor menu

Proven in the parts editor: a frozen-view cursor menu (knowledge/frozen-view-mouse-input-with-packetevents.md, knowledge/screen-panel-from-glyph-tiles-on-text-displays.md) with a clear window in its panel, a copy of a crate that only the admin sees standing behind it, X/Y/Z arrows on the selected part with clickable labels at their tips, and a top view where the camera moves above the copy and the whole panel tilts to face it.

## The window

- Paint the window into the screen's baked art with `AlphaComposite.Clear` (a rounded rectangle), then draw its border. The tiles over it are transparent there, so the world behind the panel shows through. No new glyphs are needed.
- The world shows through as it is: other crates' holograms and the time of day included. Give the preview's display entities full brightness (`Display.Brightness(15, 15)`) so it reads at night.

## Projection (world point to virtual pixel, and back)

The fit (knowledge/screen-panel-from-glyph-tiles-on-text-displays.md) makes the panel exactly fill the window, so the camera's field of view is known without asking the client:

- Camera basis: `forward = eye.getDirection()`, `right = (-forward.z, 0, forward.x)` normalised (kept level, so no roll), `up = right × forward`.
- Blocks per virtual pixel at 1 block: `perPixel = UNIT / fitDistance`, with `UNIT = 2 · 2 · tan(35°) / 1080` from `VirtualScreen`.
- A point P: `r = P − eye`, `depth = r · forward`; `vx = 960 + (r · right) / depth / perPixel`, `vy = 540 − (r · up) / depth / perPixel`.
- A ray through (vx, vy): `forward + right · (vx − 960) · perPixel + up · (540 − vy) · perPixel`, normalised.
- Place the copy on the ray through the window's centre, lowered by half its height, at the distance where its size fills at most ~70% of the window: `distance = size / (0.7 · windowPixels · perPixel)`, at least 3 blocks. At a fixed 4.5 blocks a 1.7-block crate overflowed a 262-pixel-high window.
- Measured: labels drawn at the projected arrow tips landed on the tips, level and at pitch 62.

## Moving the camera and tilting the panel

- Teleport the existing client-only camera display (`WrapperPlayServerEntityTeleport` with the new yaw and pitch, both on the 360/256 byte grid). The view cuts there with no smoothing, and there's no eye-height ease (that only happens on the first freeze).
- A level panel's maths needs three changes for a pitched camera:
  - Text displays get pitch `−cameraPitch` (with yaw `cameraYaw + 180`), because a fixed display is oriented `rotationYXZ(−yaw, pitch, 0)`.
  - Item displays (icons) get pitch `+cameraPitch` with yaw `cameraYaw`.
  - Positions use the camera's `up` vector instead of world Y.

  With pitch 0 all three reduce to the level panel, so existing menus are unaffected.
- Put the camera back before the next screen draws (the menu framework draws from the camera's current eye). A server-side teleport closes cursor menus, but this is client-only, so it doesn't.
- Item icons are shaded by the game's directional item lighting, so the same icon is darker level and lighter when the camera looks down. It isn't a projection fault.

## The preview copy

- Spawn each block, item and entity part with `setVisibleByDefault(false)` in the spawn consumer, then `player.showEntity(plugin, entity)`. Models use the provider's viewer argument.
- Rebuild the whole copy on every change. It's a few dozen entities for one viewer, and the load run above shows no cost.
- Remove the copy whenever the screen stops showing. Cursor menus already end sessions on quit, death, damage, teleport, world change and plugin disable, and every screen's `hidden()` runs then. That is what keeps it leak-free: `setPersistent(false)` only covers crashes.
- **Highlight:** `setGlowing(true)` plus `Display#setGlowColorOverride` for display parts. A plain mob glows white (a coloured glow needs a team). A model handle has no glow, so box it with thin rods.
- **Glow outlines draw over the panel.** They're blended in after the world, so an outline outside the window shows on top of the cards. Keep glowing things inside the window: the copy's fit does this for parts, but an arrow pointing out of the window still spills.
- **Arrows:** use thin block-display rods with a cube head, full-bright and glowing in their axis colour. Size their length to the copy (0.45 × its extent, 0.6–2 blocks). At 0.6 blocks and unlit they were unreadable at night.
- **Hitbox outline:** size it after the parts spawn. A plain entity's box is only known once it's in the world, and sizing it before spawning drew it one block too small.

## Panel layers

A selected row's tint on the same layer as the pills over it z-fought, which showed as half-dim pills. A layer between the tiles and the shapes (`UNDER`) fixed it level (verifier PASS). A faint seam on the selected row's bottom edge was still visible in the tilted top view.

## Not yet proven

- Clicking the arrows and the view buttons (the test client can't click; views were opened with `/sc parts <crate> top`).
- Side view and the ↺ ↻ turns in game.
- Model parts in the preview (the test crate has none).
