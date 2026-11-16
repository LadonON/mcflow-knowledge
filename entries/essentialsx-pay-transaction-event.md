---
title: "Reacting to EssentialsX /pay with TransactionEvent"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "server/screenshots/payping/real-pay-settled.png and stack-max-four.png (bot cobhaa running /pay Doom_950 <n>); EssentialsX 2.22.0"
sources:
  - "EssentialsX-2.22.0.jar: net.essentialsx.api.v2.events.TransactionEvent, com.earth2me.essentials.CommandSource (javap)"
  - "https://github.com/EssentialsX/Essentials/releases/tag/2.22.0"
  - "research/EssentialsX Pay Event and PacketEvents for 26.3.md"
date: 2026-11-16
---

# Reacting to EssentialsX /pay with TransactionEvent

- EssentialsX 2.22.0 loads and runs on Paper 26.3. It logs "You are running an
  unsupported server version!" once at startup; /pay, /eco and balances work.
- `net.essentialsx.api.v2.events.TransactionEvent` fires once per receiver,
  after the money has moved: `getRequester()` (a `CommandSource`;
  `getPlayer()` is null for the console), `getTarget()` (an `IUser`;
  `getBase()` is the Bukkit player), `getAmount()` (`BigDecimal`). It is not
  cancellable. Fired from /pay on the main thread; check `isAsynchronous()`
  anyway and hop to the main thread if another plugin calls `payUser` off it.
- Compile against the jar the server runs (`compileOnly files(...)`): the Maven
  repository's releases stopped at 2.21.2.
- Without a permissions plugin, players need op for /pay.
- Turn off what reports to third parties on a test server: `update-check: false`
  in `plugins/Essentials/config.yml` and `enabled: false` in
  `plugins/bStats/config.yml`. Both are on by default.
