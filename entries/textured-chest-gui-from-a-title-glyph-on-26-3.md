---
title: "Textured chest GUIs drawn by a font glyph in the title on 26.3"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/custom-chest-ui-probe/rows-6-scale-default.png, rows-3-scale-default.png; server/screenshots/chest-skins/*.png (preview, crates, keys, history, reel opening); ChestSkinsTest (8 tests); verifier-visual pass after the label-plate fix, 2026-11-28"
sources:
  - "research/Textured Chest GUIs with Font Glyph Titles on 26.3.md"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/entity/Player.html"
  - "https://mojira.dev/MC-299025"
date: 2026-11-28
---

# Textured chest GUIs from a title glyph

Proven with SuperiorCrates' chest skins (`menu/skin/`): one picture per row count, drawn behind a vanilla chest window.

## What works

- **Layering:** items draw on top of a full-window title glyph on 26.3. MC-299025 (the glyph covering items) doesn't happen.
- **Position:** the title's pen starts 8 px right of the window's left edge, and the glyph's top is at `13 - ascent` from the window's top. With `ascent = 13`, a picture's row 0 lines up with the window's top edge. Slot cells drawn at x `7 + 18c`, y `17 + 18r` (menu) and `H - 84 + 18r`, plus 4 for the hotbar (player inventory), match the items exactly. H is `114 + 18 × rows`.
- **Advance:** after the glyph the pen moves by (rightmost column with any alpha) + 2. A 184 px opaque picture moved it 185.
- **Shifts:** a `space` provider with ±1, 2, 4, … 256 advances, combined per bit, moves the pen anywhere. Negative advances load fine.
- **Colour:** give the glyph's component the colour white, or the title's default `#404040` darkens it.
- **Who gets it:** `Player#getResourcePackStatus()` returns `SUCCESSFULLY_LOADED` for the pack set in server.properties. That pack is sent during configuration, and no `PlayerResourcePackStatusEvent` fired for it, so tracking the event alone left everyone plain. Players without the pack get the plain title.

## Gotchas

- **Cover the whole window.** Any transparent pixel over the vanilla window shows vanilla's frame through it. 2 px gaps between tab pieces showed up as white bars until the window rectangle was filled first.
- **Nothing above a 6-row window.** At 1280x720 on Auto (240 GUI px tall) a 6-row window has 9 px spare; a 14 px tab above it was clipped. Put the title tab inside the window's 17 px title strip.
- **The "Inventory" label can't be moved or recoloured.** It's always drawn `#404040` at (8, H-94), so give it a light plate at least 51 px wide (the word is 50 px in the Minecraft font).
- **Centring titles:** the server can't measure client text, so use the default font's advance table (most letters 6, `i`/`!`/`.` 2, `l` 3, `I`/`t` 4, `f`/`k` 5, space 4). With Force Unicode on, centring can be off by a few px.
- **One glyph per picture:** a picture must fit one 256 x 256 font atlas page. A 6-row skin, 184 x 226, fits.
- **MockBukkit 4.124:** `Player#getResourcePackStatus()` throws `UnimplementedOperationException`, and MockBukkit reports that as a *skipped* test, not a failure. Count skipped tests, or a green run can hide it.
