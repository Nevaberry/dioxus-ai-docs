# Testing and local development

## Workers Vitest configuration

Workers Vitest 4 uses a configuration plugin. Install `vitest@^4.1.0` together
with `@cloudflare/vitest-pool-workers`, add `cloudflareTest()` to the Vite plugin
list, and point it to the Wrangler configuration that declares the Durable
Object bindings and lifecycle configuration.

```ts
export default defineConfig({
  plugins: [
    cloudflareTest({
      wrangler: { configPath: "./wrangler.jsonc" },
    }),
  ],
});
```

## Typed test bindings

Include `@cloudflare/vitest-pool-workers/types` in the test TypeScript
configuration. Augment `cloudflare:workers` so the test runtime's `env` exposes
the project's binding types.

```ts
declare module "cloudflare:workers" {
  interface ProvidedEnv extends Env {}
}
```

## HTTP and direct-stub integration tests

Call `exports.default.fetch()` to exercise the default Worker's HTTP handler and
its routing to a Durable Object. Use the namespace binding from `env` when a test
needs to invoke a Durable Object stub directly.

```ts
const response = await exports.default.fetch(
  "http://example.com?id=http-test",
  { method: "POST" },
);
```

## Storage lifetime and test isolation

Repeated access to the same named object across tests in one file observes
earlier stored data. Different IDs have independent storage. Evicting all
instances does not delete persisted test storage, so use distinct names when a
test requires isolated state.

## Alarm tests

`runDurableObjectAlarm(stub)` immediately executes a scheduled future alarm and
returns `true`. It returns `false` if no alarm remains.

```ts
const ran = await runDurableObjectAlarm(stub);
expect(ran).toBe(true);
expect(await runDurableObjectAlarm(stub)).toBe(false);
```

## Eviction tests

`@cloudflare/vitest-pool-workers` 0.16.20 and later exports
`evictDurableObject` and `evictAllDurableObjects` from `cloudflare:test`
(since 2026). Targeted eviction normally simulates WebSocket hibernation; pass
`{ webSockets: "close" }` to test the non-hibernating path.

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

Before tearing down an instance, `evictDurableObject()` waits up to 30 seconds
for in-flight requests to drain. It clears in-memory instance state but retains
durable storage.

## `wrangler dev` persistence boundary

Without an explicit cross-script binding, `wrangler dev` can read Durable
Object storage while keeping writes in memory instead of changing persistent
data. If a binding explicitly sets `script_name`, development writes do affect
persistent storage, and Wrangler emits a warning.
