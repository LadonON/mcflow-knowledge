---
title: "Screen-filling panels from bitmap glyph tiles on text displays (frozen camera)"
minecraft_versions: ["26.3"]
pack_format: 97
paper_api_version: "26.3"
verified_by: "server/screenshots/phase3-cursor-render/*.png (FrozenViewProbe, 2026-11-26); server/screenshots/phase3-admin-menu/admin-near-panel.png, admin-reverify.png (SuperiorCrates /sc admin, verifier-visual PASS); gate_performance admin-menu (10 bots, 144 opens/min, median 12.0 ms) and gate_memory (no leaks), 2026-11-26; server/screenshots/phase3-crate-editor/editor-open-3.png (item icons), gate_performance crate-editor (10 opped, fitted bots, 141 opens/min, median 4.8 ms vs 5.8 ms idle), gate_memory crate-editor (7 cycles, no leaks), 2026-11-26; server/screenshots/reward-editor/five-actions-fixed.png and reverify-after-humanize.png (dithered glow, verifier-visual PASS), 2026-11-27"
sources:
  - "research/Bitmap Font Glyphs on Text Displays on 26.3.md (26.3 client jar: TextDisplayRenderer, Font, core/text.fsh)"
  - "research/Layering Display Entities as a Screen-Fitted Panel on 26.3.md (26.3 client jar: GameRenderer, Camera, ClientLevel)"
date: 2026-11-26
---

# Screen-filling panels from bitmap glyph tiles on text displays

Proven: a 1920x1080 picture drawn as 40 glyph tiles on text displays, on a plane in front of a client-only camera (see `frozen-view-mouse-input-with-packetevents.md`). The tiles join without seams, colours match the source PNG, a text layer in front draws over them, and a see-through cursor stays on top.

## Tiles

- **Cutting:** cut the picture into tiles of 256x256 or smaller (font atlas pages are 256, so a bigger glyph cell can't bake). Give each tile one `bitmap` provider with `height` = the tile's pixel height and `ascent` 0. One font pixel is then one tile pixel.
- **Pitfall, mostly transparent tiles:** a bitmap glyph is only as wide as its last non-transparent column, and a text display centres its text on that width. A tile that's mostly transparent shrinks and slides sideways. Fix it by writing a pixel with alpha 1 into the tile's rightmost column. That alpha is below the shader's discard threshold, so it's invisible.
- **Alpha:** the text shader discards fragments with alpha below 0.1 (26/255). Faint glass painted on its own vanishes, so bake translucency onto its background and ship the tiles opaque.

## Size and placement

- **Font pixel size:** one font pixel is 0.025 blocks on a text display at scale 1.
- **Scale:** to make one virtual pixel `UNIT` blocks, use display scale `UNIT / 0.025`.
- **Screen size at FOV 70:** the screen fills the view at distance `d` when `UNIT = 2·d·tan(35°) / 1080` (FOV 70 is vertical). At d = 2 that's 2.8008 x 4.9793 blocks.
- **Anchoring:** with ascent 0, a single glyph's top edge is 2 font pixels above the display's position, and its centre is half a font pixel right of it. Place each tile at virtual (tile centre x − 0.5, tile top + 2).
- **Display settings:** text displays need `lineWidth` set huge (100000) so wide glyphs never wrap. Use background ARGB 0, shadow off, billboard FIXED with yaw = camera yaw + 180, and brightness 15/15. Colours came out as in the PNG with `see_through` off.
- **Layering:** spawn back to front. A text layer 0.002 blocks toward the camera drew cleanly over the tiles. A `see_through` display, used for the cursor, is drawn last, on top of everything.

## Fit

- **Fitting the frame:** the server can't read FOV or window shape, so you fit by distance. Move the panel back until the frame's corners touch the screen edges.
- **Measured:** at FOV 70 in a 1920x1174 window (aspect 1.635), the 16:9 panel fit at d = 2.18, which is 2 × (1920/1174) / (16/9). That matches the maths exactly.
- **Gaps:** when the window is narrower than 16:9 the fit leaves bands above and below. Extend the backdrop past the panel so those bands aren't world.

## In production (the SuperiorCrates admin menu)

- **Client-only packet entities, not real entities.** Real text displays cost about 93 ms to spawn 250 in one tick, and the server tracks them every tick afterwards. Sending `SpawnEntity` and `EntityMetadata` packets with PacketEvents to the one player leaves the server holding nothing.
- **TextDisplay metadata indexes on 26.3**, read from the server jar's static initialisers:

  | Index | Field |
  |---|---|
  | 10 | position/rotation interpolation (int) |
  | 12 | scale (Vector3f) |
  | 15 | billboard (byte, 0 = fixed) |
  | 16 | brightness (int, `15<<4 \| 15<<20`) |
  | 23 | text (component) |
  | 24 | line width |
  | 25 | background (int, 0 = none) |
  | 26 | opacity (byte) |
  | 27 | style flags (0x02 = see-through) |

  Entity owns indexes 0-7 and Display owns 8-22. To hide an element, set its scale to 0.
- **Spread the work over ticks.** Building and encoding a 212-element screen took 25-40 ms on the main thread once warm, and about 180 ms on the first open after a restart. Flushing per packet was not the cost. Queue the packet builders and send them within about 3 ms a tick, tiles first. Measured: the open tick about 8 ms, then 3 ms a tick for a few ticks. A swarm of 10 bots opening it 144 times a minute ran at a median of 12.0 ms against 15.1 ms with the same bots idle.
- **Yaw grid.** Spawn packets send yaw as a byte (360/256 degrees per step). Start the camera and the panel from a yaw already on that grid, or the panel looks slightly turned. A user spotted this in game.
- **Draw it near.** Nearby blocks (a tree 1-2 blocks away) and rain drew over a panel at 2 blocks. Place it at 0.2 times its nominal distance, scaled by 0.2 too: it looks identical, and nothing gets between it and the camera. `setPlayerWeather(CLEAR)` while it's open, then restore the player's own weather.
- **Sliced images** (3-slice pills): clip each slice's painting to its own size before stretching. Otherwise the padding is painted too and the stretch smears the slice far past the pill.
- **Departed players.** PacketEvents' `getUser(player)` is null once a player has left. Guard every send, and end a session in `finally`, or a menu that's drawing as its player quits stays in memory.
- **Share one send budget across all open menus.** A budget per menu (3 ms each) adds up when several menus draw at once. Give all menus 4 ms a tick together: each gets at most 3 ms, and at least 0.2 ms so its cursor keeps moving. Rotate who goes first each tick. Under load, screens then take a few ticks longer to appear instead of slowing the server. Measured with the crate editor (271 elements, 2–4 ms to build once warm): 10 bots opening it 141 times a minute gave a median of 4.8 ms and p95 of 11.2 ms, against 5.8 ms and 10.9 ms with the same bots idle.

- **Soft glows need dithering, not alpha.** A live glow (tinted per use, so it can't be baked into the tiles) painted as a radial alpha fade ends in a hard circle where the alpha crosses the shader's 26/255 cut: rings at alpha 28 or more read as a flat disc. Instead set each pixel either clear or to one fixed alpha (64 worked), with a 4x4 Bayer threshold so fewer pixels are set further from the centre: `density = (1 - r/R)^1.6`, pixel set when `density * 16 > bayer + 0.5`. At panel scale it reads as a soft haze with no edge (verifier-visual PASS, `server/screenshots/reward-editor/reverify-after-humanize.png`). Alpha 120 dots showed as a visible dot grid.
- **Inter's space after a digit** is narrow at Medium 17 ("1 problem" read as "1problem" to the verifier). Two spaces fix it.
- **Regenerated art needs a version bump.** If the pack writer skips repainting when its signature (art version + glyph count) is unchanged, a repainted glyph with the same count ships the old picture. Bump the art version with any art change, and check the served pack's SHA-1 changed.

## Item icons on the panel

Proven in the crate editor (`server/screenshots/phase3-crate-editor/editor-open-3.png`): a reward's real item (diamond, netherite sword) drawn as an inventory icon, facing the camera, on the text layer.

- **Entity:** a client-only `ITEM_DISPLAY`, spawned with PacketEvents like the text displays.
- **ItemDisplay metadata indexes on 26.3**, read from `Display$ItemDisplay` in the server jar: 23 is the item (`ITEMSTACK`, converted with `SpigotConversionUtil.fromBukkitItemStack`), 24 is the display context (byte). Context 6 is `GUI`, which poses the item as an inventory slot shows it, so block items appear in 3D.
- **Facing:** an item display draws its item turned half a turn, so its yaw is the camera's yaw, not the camera's yaw + 180 used for text displays.
- **Size:** an item is one block across at scale 1, so scale = icon size in virtual pixels × blocks per virtual pixel (at the near distance, shrunk by the layer's perspective like the other layers). Position it at the icon's centre: an item display pivots on the item's centre.
- **Brightness:** the same full-bright override (index 16) as the text displays.

## Load-testing menus with bots

- **Admin permission:** cursor menus need an admin permission, and test bots aren't ops, so the command is silently refused. Op the bots (Perf0–Perf9, Mem0–Mem4) for the run and de-op them after.
- **Fit screen:** a player who has never fitted the panel sees the fit screen, which only takes mouse clicks, so bots never get past it. Set each bot's fit once with `/sc menufit 2.0` (the fit is saved on the player). Without both steps, a run measures a refused command or the fit screen, not the menu.
- **Warm-up:** the first run after a restart includes JIT warm-up (worst ticks of 0.6–1.7 s). Do a throwaway run first, then the idle baseline and the feature run back to back.

## Still unproven

- Other FOVs and aspect ratios, beyond the maths. The one-time fit step lets each player correct for these by hand.
- Fast and Fabulous graphics.
- F5 while open.
- The camera's eye-height settle, frame by frame.
- Load with many displays.
