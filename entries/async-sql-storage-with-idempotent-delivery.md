---
title: "Async SQL storage (SQLite/MySQL/PostgreSQL) with duplicate-proof reward delivery"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "plugins/SuperiorCrates StorageTest (8 tests) and SuperiorCratesPluginTest; gate_thread_safety pass, gate_memory pass and gate_performance pass (20 bots, 285 openings/min) on 2026-11-24"
sources:
  - "https://www.sqlite.org/wal.html"
  - "https://github.com/xerial/sqlite-jdbc (pragmas as connection properties)"
  - "research/Async Database Stack for Paper Plugins.md"
date: 2026-11-24
---

# Async SQL storage with duplicate-proof reward delivery

## Threads

All SQL runs in `CompletableFuture.supplyAsync(..., dbExecutor)`. Results hop back with `thenApplyAsync(fn, mainThread)`, where `mainThread` runs the task immediately if already on the server thread, else `Bukkit.getScheduler().runTask`, and drops it once the plugin is disabled.

## SQLite

- **Pool:** HikariCP with `maximumPoolSize = 1` and a single-thread executor. SQLite allows one writer anyway.
- **Pragmas:** pass them as data-source properties: `addDataSourceProperty("journal_mode", "WAL")`, `("synchronous", "FULL")`, `("busy_timeout", "5000")`. sqlite-jdbc runs only the first statement of a multi-statement `connectionInitSql`.
- **Errors:** sqlite-jdbc leaves `SQLState` null on constraint errors. Match `SQLITE_CONSTRAINT` in the message. Other drivers use SQLState class `23`.

## Portable SQL

- **No upserts:** avoid upserts and `RETURNING`, which differ between SQLite, MySQL and PostgreSQL. Use `UPDATE`, and if no row changed, `INSERT`. On a primary-key clash, throw a retry exception, roll back and rerun the whole transaction (3 attempts).
- **Indexes:** MySQL has no `CREATE INDEX IF NOT EXISTS`. Create indexes inside a numbered migration that runs once.

## Exactly-once delivery

- **Claiming a row:** each owed reward is a row with a state. A server claims it only with `UPDATE ... SET state='DELIVERING' WHERE id=? AND state='PENDING'` and acts only if one row changed. 20 concurrent claims of one row: exactly 1 wins (StorageTest).
- **Opening transaction:** in one transaction, take the key, check the cooldown, choose rewards with fresh limit counts, count limited wins, insert the opening and its delivery rows (already DELIVERING), and commit. Any failure rolls everything back, so nothing is spent.
- **Key takes:** use `UPDATE keys SET amount = amount - ? WHERE ... AND amount >= ?`. 200 concurrent takes of a 50-key balance: exactly 50 succeed (StorageTest).
- **Interrupted deliveries:** at startup, rows still DELIVERING for this server-id become UNCERTAIN instead of being redelivered. The server may have stopped after giving the item but before recording it.

## Pitfalls

- **Unwrapping failures:** `CompletableFuture.get()` unwraps a `CompletionException` thrown inside the supplier. The `ExecutionException`'s cause is the inner exception.
- **Cold start:** the first openings after a restart, with class loading and the first limit-row insert, took over 1 s once, and a per-player "opening in progress" guard rejected a command sent 1 s later. Later openings were fast. Log openings slower than 250 ms, split into queue wait and transaction time.
