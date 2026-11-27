---
title: "MiniMessage name placeholders without colour leaking into the message"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/phase1-core/chat-keys-open-claim.png (leak) vs chat-after-fix.png (fixed); MessageFormatterTest.nameColoursDoNotLeakIntoTheRestOfTheMessage"
sources:
  - "https://docs.advntr.dev/minimessage/dynamic-replacements.html"
date: 2026-11-24
---

# MiniMessage name placeholders without colour leaking into the message

## The leak

`Placeholder.parsed("reward", "<green>500 XP")` splices the raw tags into the template. The `<green>` stays open, so in `You won <reward> from <crate>!` the words " from … !" turned green in game.

## The fix

Parse admin-written names separately, and insert them as a component:

```java
Placeholder.component("reward", MiniMessage.miniMessage().deserialize(displayName))
```

The name keeps its own colours, including gradients, and the rest of the line keeps the template's colour.

## Related rules

- **Player text:** names and anything else a player types go in with `Placeholder.unparsed`, so `<red>` in a name prints as text.
- **Legacy hex:** `&#RRGGBB` codes aren't MiniMessage. Convert them with `&#([0-9a-fA-F]{6})` → `<#$1>` before parsing. Proven with the SuperiorCrates prefix in game.
- **Open tags in a prefix:** a prefix that ends in an open tag (`… >> <white>`), meant to colour the message body, has to be spliced into the template as text before parsing, not inserted as a component.
