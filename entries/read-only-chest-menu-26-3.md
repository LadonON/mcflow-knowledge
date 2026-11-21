---
title: "Read-only chest menus (recipe viewer) on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "In game 2026-11-21: the recipe viewer opened on the real client (server/screenshots/recipe-viewer/viewer-milling.png, viewer-sequenced.png; verifier-visual passed both against layouts/recipe-viewer.layout.md); a bot's shift-click and number-key click left its inventory unchanged, Close closed it; the session was dropped when the bot left; gate_memory passed"
sources:
  - "research/Inventory Menu GUIs on Paper 26.3.md"
date: 2026-11-21
---

# Read-only chest menus on Paper 26.3

`createpaper.viewer.RecipeViewer`:

- `Bukkit.createInventory(holder, 54, Component title)` with the session as the `InventoryHolder`.
- Cancel every `InventoryClickEvent` (LOWEST priority) whose *top* inventory's holder is the session. This includes clicks in the player's own inventory: shift-clicks from there would push items in. Cancel every `InventoryDragEvent` the same way. Proven against shift-click and number-key clicks.
- A new title needs a new inventory. Open it with `runTask` on the next tick, not from inside the click event.
- `InventoryCloseEvent` also fires when the menu is swapped for a new one. Check on the next tick whether the player's top inventory is still a session before forgetting it. Also forget it on `PlayerQuitEvent`.
- The mcflow client's `client_close_screen` doesn't seem to tell the server, which still counts the menu as open until the player leaves. That's a test-tool quirk, not a leak.

Item names and lore: `DataComponentTypes.CUSTOM_NAME` and `LORE` with italic turned off. A paper item with `ITEM_MODEL` set to a pack model makes a custom icon (the arrow).
