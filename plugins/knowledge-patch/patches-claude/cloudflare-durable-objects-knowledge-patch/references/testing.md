# Testing Durable Objects

## Configure Workers Vitest 4

Install `vitest@^4.1.0` with `@cloudflare/vitest-pool-workers`. Add
`cloudflareTest()` to the Vite plugin list and point it to the Wrangler
configuration that declares the Durable Object bindings and migrations.

```ts
export default defineConfig({
  plugins: [
    cloudflareTest({
      wrangler: { configPath: "./wrangler.jsonc" },
    }),
  ],
});
```

## Type test bindings

Include `@cloudflare/vitest-pool-workers/types` in the test TypeScript
configuration. Augment `cloudflare:workers` so the test runtime's `env` uses
the project's binding types.

```ts
declare module "cloudflare:workers" {
  interface ProvidedEnv extends Env {}
}
```

## Test the Worker or a stub at the right boundary

Use `exports.default.fetch()` to test the default Worker's HTTP handler and its
Durable Object routing. Use a binding from `env` when the test should call a
Durable Object stub directly.

```ts
const response = await exports.default.fetch(
  "http://example.com?id=http-test",
  { method: "POST" },
);
```

## Account for storage persistence and isolation

Repeated access to the same named object across tests in one file sees earlier
stored data. Distinct object IDs have independent storage. Evicting instances
does not delete this persisted data.

## Run scheduled alarms immediately

`runDurableObjectAlarm(stub)` immediately executes a scheduled future alarm and
returns `true`. It returns `false` when no alarm remains.

```ts
const ran = await runDurableObjectAlarm(stub);
expect(ran).toBe(true);
expect(await runDurableObjectAlarm(stub)).toBe(false);
```

## Exercise eviction paths

`@cloudflare/vitest-pool-workers` 0.16.20 and later exports
`evictDurableObject` and `evictAllDurableObjects` from `cloudflare:test`
(2026). The targeted helper normally simulates eviction with WebSocket
hibernation; pass `{ webSockets: "close" }` to test the non-hibernating path.

```ts
import {
  evictAllDurableObjects,
  evictDurableObject,
} from "cloudflare:test";

const stub = env.COUNTER.getByName("my-counter");
await evictDurableObject(stub);
await evictDurableObject(stub, { webSockets: "close" });
await evictAllDurableObjects();
```

Before teardown, `evictDurableObject()` waits up to 30 seconds for in-flight
requests to drain. It resets in-memory state but preserves durable storage.
`evictAllDurableObjects()` likewise resets running instances without deleting
persisted data.
