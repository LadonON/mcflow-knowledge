---
title: "Reading an item's name, lore, enchantments and model through data components on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/reward-editor/five-actions-fixed.png: the reward editor's item card and action note read CUSTOM_NAME, LORE (1 line), ENCHANTMENTS (Sharpness V), ITEM_MODEL (Default), UNBREAKABLE and TOOLTIP_DISPLAY from a field-form config item, 2026-11-27"
sources:
  - "research/Editing Reward Item Components on Paper 26.3.md (paper-api-26.3.build.261-stable.jar and paper-26.3.jar, javap)"
date: 2026-11-27
---

# Reading an item's name, lore, enchantments and model through data components on Paper 26.3

Proven in game for **reading**. Writing these components back (`setData`, `resetData`, `unsetData`, `withType`) is in the reward editor but wasn't exercised, because the test client can't click: it stays in `research/Editing Reward Item Components on Paper 26.3.md` until someone presses the buttons.

- **Components:** `DataComponentTypes.CUSTOM_NAME` (Component), `LORE` (`ItemLore#lines()`), `ENCHANTMENTS` (`ItemEnchantments#enchantments()`, a `Map<Enchantment, Integer>`), `ITEM_MODEL` (Key), `UNBREAKABLE` (non-valued: test with `hasData`), `TOOLTIP_DISPLAY` (`hiddenComponents()` holds `ENCHANTMENTS` when enchantments are hidden). Read with `ItemStack#getData`; each returns null when absent.
- **Item model:** `getData(ITEM_MODEL)` always returns a key, because every item has a default model. Use `isDataOverridden(ITEM_MODEL)` to tell a custom model from the material's own.
- **Names and lore back to MiniMessage:** text that was set with italics turned off (as config items are) serialises with a leading `<!italic>`. Strip it before showing it to an admin to edit.
- **Enchantment ids:** `enchantment.getKey()` is `minecraft:sharpness`; show the bare value for the minecraft namespace and the full key for others.
- **Config items:** an item built from config fields (`material`, `name`, `lore`, `enchantments`) reads the same as one saved with `serializeAsBytes`.
