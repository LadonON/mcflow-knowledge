---
title: "Embedded Jetty 12 web panel inside a Paper 26.3 plugin"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "PanelApiTest (MockBukkit, real HTTP), deployed on Paper 26.3 build 261 2026-11-27 (log: 'Web panel listening on 127.0.0.1:7461'); gate_performance idle 10 bots median 8.2 ms vs 8.9 baseline with 210/210 panel requests ok; gate_memory and gate_thread_safety pass"
sources:
  - "https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-server/maven-metadata.xml"
  - "https://jetty.org/docs/jetty/12.1/programming-guide/server/http.html"
  - "jetty-io-12.1.15.jar: org.eclipse.jetty.io.Content$Source (javap)"
date: 2026-11-27
---

# Embedded Jetty 12 web panel inside a Paper 26.3 plugin

## Shipping it

- List `org.eclipse.jetty:jetty-server:12.1.15` under `libraries:` in plugin.yml, and add it as `compileOnly` in Gradle, with `testImplementation` for tests.
- Paper's library loader resolves the dependencies itself: jetty-http, jetty-io and jetty-util. slf4j-api is already there.
- The first start downloads about 2.6 MB into `server/libraries/`. Nothing gets shaded.
- Paper bundles Gson, so use it for the JSON.

## Server setup

- Use the core API, not servlets: `new Server(new QueuedThreadPool(16, 2))` with the pool named `SuperiorCrates-Panel` and set to daemon, plus one `ServerConnector`.
- Call `connector.setHost("127.0.0.1")` and `setPort(...)`.
- The handler is `Handler.Abstract#handle(Request, Response, Callback)`, and it returns `true`.
- Start it in `onEnable`. If the port is taken, `server.start()` throws. Log the error and keep the plugin running without the panel.
- Stop it in `onDisable` with `setStopTimeout(2000)`. After a restart the port is free again: it was verified across several deploys.

## Threading

- Handlers run on Jetty threads. Don't block them on the main thread; reply asynchronously:
  - Return `true`.
  - Run the work as `CompletableFuture.supplyAsync(task, mainThreadExecutor)`.
  - When it finishes, call `response.write(true, ByteBuffer, callback)`.
- Read the request body without blocking: `Promise.Completable.with(p -> Content.Source.asString(request, UTF_8, p))`. `Content.Source.asStringAsync` is deprecated for removal in 12.1.15, so don't use it.
- File work stays on the plugin's IO executor and database work on its own pool. Everything from Bukkit goes through the main thread. `gate_thread_safety` found nothing.

## Useful Jetty 12.1 calls

`Request.getPathInContext`, `Request.getCookies`, `Request.getRemoteAddr`, `Request.extractQueryParameters`, `request.getHeaders().get(HttpHeader.X)`, `response.getHeaders().put/add`, `request.getLength()`.

## Serving the page

- Vite builds into `src/main/resources/web/`, which is checked in, so the plugin builds without Node.
- Serve the files with `getClassLoader().getResourceAsStream("web/" + name)` and cache them in memory.
- Fall back to `index.html` for paths with no dot. Reject paths containing `..`.
- Hashed `assets/` files get `max-age=31536000, immutable`. Everything else gets `no-store`.

## Pitfalls hit

- **Gradle opt-in flag:** `project.hasProperty('buildWeb')` is true whenever a *task* named `buildWeb` exists. Use `providers.gradleProperty('buildWeb').isPresent()`.
- **Default port:** port 8765 was taken by another program on the dev machine, so the default is 7461. Tests start the panel on a random port.
- **Stale page:** a hash-routed app keeps running old JS after a redeploy until the page reloads. When testing, load the page fresh.
