---
title: "Top-right HUD elements from boss bar text and a text.vsh core shader"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/payping/single-settled.png, stack-settled.png, stack-max-four.png (verifier-visual pass, measured margins/pitch/colours)"
sources:
  - "26.3 client jar: assets/minecraft/shaders/core/text.vsh, text.fsh, include/globals.glsl (unzip)"
  - "26.3 client jar: RenderPipelines GUI_TEXT (text snippet + IS_GUI define), boss bar overlay (javap)"
  - "research/Text Core Shader Overrides in 26.3.md"
date: 2026-11-16
---

# Top-right HUD elements from boss bar text and a text.vsh core shader

A server can draw anywhere on the HUD by sending boss bar text and moving the
glyphs in a resource-pack `assets/minecraft/shaders/core/text.vsh`. Proven in
the PayPing plugin (`plugins/PayPing/tools/text.vsh.template`).

## What holds on 26.3

- A pack's `shaders/core/text.vsh` overrides vanilla's. HUD text (boss bar names
  included) runs it with `IS_GUI` defined; wrap all changes in `#ifdef IS_GUI`
  so world text (signs, name tags) is untouched. `text.fsh` needs no change.
- `Position.xy` is already in GUI pixels (the text pose is applied on the CPU).
  The GUI width is `2.0 / ProjMat[0][0]`; the right screen edge is at that x.
- The vertex `Color` is the exact text colour in bytes: `round(Color.rgb * 255)`
  matches a marker exactly. Use red = 254 as the marker, green as a "kind", blue
  as a per-glyph y offset (0-255). Set the output colour in the vertex shader,
  since the marker colour is not the colour you want drawn.
- `shadow_color` 0 (Adventure `ShadowColor.none()`) removes the shadow quads
  entirely, so shadows can't land in the wrong place.
- Boss bar names are drawn at y = 3 + 19n, centred at
  `x = guiWidth / 2 - width / 2` (both integer divisions). Give the line a fixed
  total advance (PayPing: 512, padded with space glyphs) so its start is known:
  `lineStart = floor(ceil(guiWidth) / 2) - 256`. Then a glyph's pen position
  along the line (`Position.x - lineStart`) is free data: horizontal placement
  and slide animations are just extra space before the glyph.
- Every glyph used is 8 tall with ascent 7, so `mod(Position.y - 3, 19) > 4`
  tells a bottom vertex from a top one; stretch panels by moving bottoms only.
- Hide the bar itself: use `BossBar.Color.PINK`, `Overlay.PROGRESS`, progress 0,
  and a transparent 182x5 `textures/gui/sprites/boss_bar/pink_background.png`.
  Side effect: every pink boss bar on the server loses its background, and other
  boss bars shift down 19 px while yours is shown.
- Bitmap glyphs advance width + 1: follow each panel piece with a -1 space so
  pieces touch.
- To lay text out from the server, measure vanilla advances from
  `minecraft:font/ascii.png` (rightmost opaque column + 1, space = 4);
  `plugins/PayPing/tools/vanilla_widths.py` does it.

## Performance (measured)

50 bots each triggering a toast every ~4 s (750 in 60 s), with frames sent
every tick only while something slides: median tick 9.2 ms vs 10.4 ms without
the plugin, p95 21.7 vs 21.9 ms.

## Not proven

- Players with "Force Unicode Font" on: text widths differ from ascii.png, so
  panel width could be off by a few px.
- Any GUI text that happens to use a colour with red = 254 is moved too.
- GUI scales other than 3 (window 1920x1174) were not screenshotted.
