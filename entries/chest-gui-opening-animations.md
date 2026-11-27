---
title: "Animated chest-GUI crate openings (reel and flip cards) on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/phase2-finish/gui-reel-spinning.png, gui-reel-result.png, gui-cards-flipping.png, gui-cards-result.png; AnimationGuiTest (3 tests); gate_performance phase2-reel (20 bots, about 20 concurrent sessions, median 6.1 ms, p95 18.4 ms); gate_memory pass with bots leaving mid-animation (2026-11-25)"
sources:
  - "https://jd.papermc.io/paper/26.3/org/bukkit/inventory/InventoryHolder.html"
  - "https://jd.papermc.io/paper/26.3/org/bukkit/event/inventory/InventoryCloseEvent.html"
date: 2026-11-25
---

# Animated chest-GUI crate openings

Proven with SuperiorCrates' GUI reel (a middle row that scrolls and slows onto the winner) and flip cards (seven cards flipping one by one).

## Building it

- **Owning the inventory:** create it with `Bukkit.createInventory(holder, 27, title)`, where `holder` is your own `InventoryHolder`. Your listeners then recognise it with `event.getInventory().getHolder(false) instanceof YourGui`. Pass `false` so Paper doesn't build a snapshot.
- **Locking it:** cancel `InventoryClickEvent` and `InventoryDragEvent` at LOWEST for that holder. Shift-clicks and number-key swaps go through the same click event.
- **Animating it:** drive frames from the plugin's single opening ticker. Call `inventory.setItem` for the slots that changed, and only on ticks where the reel actually moves. Writing all 27 slots per move was fine at 20 concurrent sessions.
- **Frame panes:** set `meta.setHideTooltip(true)` so hovering a frame shows nothing.
- **Non-item rewards** (XP, commands): show a stand-in item whose `itemName` is the reward's display name, so tooltips read right.

## Closing

- **Player closes it (Esc):** handle `InventoryCloseEvent` at MONITOR and treat it as a skip that delivers at once.
- **Plugin closes it:** set a flag before your own `closeInventory(Reason.PLUGIN)` so that close isn't taken as a skip. Proven server-side with MockBukkit: `player.closeInventory()` finishes the session once, and the plugin's own close doesn't.
- **Not proven in game:** a real Esc. The mcflow client tool's `client_close_screen` closes the screen on the client only and the server never hears about it, so this path still needs a person to press Esc once.

## Timing

- **Reel slowdown:** an ease-out cubic on position. Move *i* of *n* happens at `round(D * (1 - cbrt(1 - i/n)))`, clamped so no two moves share a tick and the last lands on D. 40 moves over 120 ticks starts at about a move per tick and ends at about 9 ticks per move.
- **Getting the winner on the marker:** build the strip as `shifts + visible` items with the winner at index `shifts + visible/2`.
