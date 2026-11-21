---
title: "Hold-to-use custom items with the consumable component on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "In game 2026-11-21: a mineflayer bot (joined as 26.1 through ViaBackwards) holding Create sand paper with 2 rose quartz in its off hand held use for 2.5 s; the off hand went to 1, polished_rose_quartz appeared in its inventory, the sand paper stayed with damage 1 of 8 (data get entity)"
sources:
  - "paper-api 26.3.build.253: io.papermc.paper.datacomponent.item.Consumable and Consumable$Builder, consumable.ItemUseAnimation, org.bukkit.event.player.PlayerItemConsumeEvent (javap)"
  - "research/Hold-to-use Items with the Consumable Component on Paper 26.3.md"
date: 2026-11-21
---

# Hold-to-use custom items with the consumable component on Paper 26.3

A paper-based item gets a hold-to-use action from the consumable data component:

```java
stack.setData(DataComponentTypes.CONSUMABLE, Consumable.consumable()
        .consumeSeconds(1.6f)                       // Create's sand paper: 32 ticks
        .animation(ItemUseAnimation.BRUSH)
        .sound(Key.key("minecraft", "item.brush.brushing.generic"))
        .hasConsumeParticles(false)
        .build());
```

When the use finishes, `PlayerItemConsumeEvent` fires with `getHand()`. Cancel it and the item isn't eaten. Then do the item's effect yourself (here: polish one item from the other hand and `ItemStack#damage(1, player)` the paper).

Uses that wear out: `MAX_DAMAGE` plus `DAMAGE` 0, with `MAX_STACK_SIZE` 1. An item can't be both damageable and stackable.

Not proven: what the brush animation looks like on the real 26.3 client (no screenshot yet), and starting the use with nothing in the other hand (the animation should still play, then nothing happens).
