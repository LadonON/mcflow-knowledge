---
title: "Brigadier command with an alias on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/scaffold-smoke-test/sc-alias-reply.png; server log 2026-11-24 10:19 'Registered command labels: [superiorcrates:superiorcrates, superiorcrates, sc, superiorcrates:sc]'; in-game /sc open, /sc keys, /sc claim in server/screenshots/phase1-core/"
sources:
  - "paper-api 26.3.build.261 (javap): io.papermc.paper.command.brigadier.Commands#register(LiteralCommandNode, String, Collection)"
  - "https://docs.papermc.io/paper/dev/command-api/basics/introduction"
date: 2026-11-24
---

# Brigadier command with an alias on Paper 26.3

## Registering

In a plain `plugin.yml` plugin, register in `onEnable`. Declare no `commands:` entry for it.

```java
getLifecycleManager().registerEventHandler(LifecycleEvents.COMMANDS, event -> {
    LiteralCommandNode<CommandSourceStack> root = Commands.literal("superiorcrates")
            .requires(source -> source.getSender().hasPermission("superiorcrates.command"))
            .then(...)
            .build();
    Set<String> labels = event.registrar().register(root, "description", List.of("sc"));
});
```

- **Labels:** `register` returns the labels that took. On 26.3 that's `[superiorcrates:superiorcrates, superiorcrates, sc, superiorcrates:sc]`. If `sc` is missing from the set, another plugin owns the alias. Check for that and log it.
- **Player arguments:** `ArgumentTypes.player()` works for a single player. Resolve it with `context.getArgument("player", PlayerSelectorArgumentResolver.class).resolve(context.getSource()).getFirst()`.
- **Gating:** `.requires(...)` on a literal hides the subcommand from players without the permission.

## Pitfalls

- **RCON replies:** RCON only captures output sent while the command runs. A reply sent later, from a future that completes on the next tick, never reaches the RCON caller. It does reach in-game senders.
- **Testing:** MockBukkit 4.124.0 doesn't expose lifecycle-registered commands (see `mockbukkit-26-3-test-setup.md`). Keep the command tree thin, and test the services it calls.
