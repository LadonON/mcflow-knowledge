---
title: "Chest GUIs that load their contents from the database without blocking the main thread"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "PlayerMenusTest (13 tests); server/screenshots/phase3-player-guis/*.png; bot GuiBot claim, Claim All and withdraw checks; gate_performance phase3-player-preview and phase3-player-history (20 bots, median 8.0 and 8.7 ms), gate_memory and gate_thread_safety pass, 2026-11-27"
sources:
  - "https://jd.papermc.io/paper/26.3/org/bukkit/inventory/InventoryHolder.html"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/event/inventory/InventoryClickEvent.html"
  - "knowledge/chest-gui-opening-animations.md"
date: 2026-11-27
---

# Chest GUIs backed by database reads

Proven with SuperiorCrates' player GUIs (preview, crates, keys, claim, history). Builds on `chest-gui-opening-animations.md` for the holder and click locking.

## Loading

- **Open first, fill later:** open the inventory at once with a "Loading…" item in the middle of the content area, run the query on the database threads, then draw on the main thread.
- **Hop back on success and failure:** `thenApplyAsync(..., mainThread)` doesn't hop when the source future fails; the failure completes on the database thread. Use `whenComplete` and run the body through the main-thread executor yourself, so a failed query can still draw a "Couldn't load" item safely.
- **Only draw into a menu that's still open:** compare `player.getOpenInventory().getTopInventory() == menu.inventory` before drawing. The player may have closed it or opened another menu while the query ran.
- **Redraw in place:** clear the inventory and the slot-to-action map and draw again on the same inventory. Opening a new one resets the cursor position.
- **One request in flight per menu:** a `busy` flag set while a click's database work runs, with further clicks ignored, stops click spam from queueing queries. 20 bots opening a menu every 3 s added about 3.5-4 ms to the median tick (idle 4.5 ms).

## Giving things from a GUI

- **Claim one row:** do the conditional state change (`UPDATE ... WHERE id = ? AND state = ?`) first, and give the item only if this call won it. A double click claimed exactly once on a real server.
- **Virtual to physical keys:** take the balance first with a conditional update, then `addItem` on the main thread, and give any leftover back to the balance. Check free room before taking, so a full inventory is refused up front.
- **Show the stored amount:** a stored item reward already has its rolled amount; show that as the icon's stack size, not the config's template item.

## Testing

- **MockBukkit 4.124:** `player.getOpenInventory().getTopInventory()` is null when no inventory is open (a real server returns the crafting grid). Null-check it in code that scans players, such as a close-all on disable.
- **mineflayer bots:** a cancelled click on a bar pane shows the pane on the bot's own cursor, but the server gives nothing (confirmed with `/clear <bot> black_stained_glass_pane 0`). The bot's chat capture misses plugin messages here, and its `attack` didn't register on an `Interaction` hitbox, so left-click-to-preview on a model crate is still unproven in game.
