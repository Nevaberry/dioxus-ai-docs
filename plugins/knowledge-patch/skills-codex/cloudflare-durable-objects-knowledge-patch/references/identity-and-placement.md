# Identity and placement

## Named identity

An object reached with `idFromName()` or `getByName()` can read the originating
name from `ctx.id.name` (since 2026), including inside its alarm handler. The
property is `undefined` for IDs created by `newUniqueId()`, access through
`idFromString()`, and names longer than 1,024 bytes.

```js
export class ChatRoom extends DurableObject {
  getRoomName() {
    return this.ctx.id.name;
  }
}
```

## Jurisdiction-scoped namespaces

Use `namespace.jurisdiction("us")` to constrain an object's compute and stored
data to the United States (since 2026). Workers outside the US can still access
the object.

```js
const usObjects = env.MY_DURABLE_OBJECT.jurisdiction("us");
const stub = usObjects.getByName("general");
```

The `eu`, `us`, and `fedramp` scopes each have a distinct ID space. The same
name produces a different ID in every scope, and a scoped namespace rejects an
ID from another jurisdiction. An unscoped namespace can resolve a restricted
ID. Prefer namespace scoping to per-ID `newUniqueId({ jurisdiction })`; an ID
can still be logged outside its jurisdiction for billing and debugging.

```js
const euRooms = env.ROOMS.jurisdiction("eu");
const euId = euRooms.idFromName("lobby");
const stub = env.ROOMS.get(euId);
```

Inside the object, `ctx.id.jurisdiction` reports the scope and survives
`toString()` followed by `idFromString()`. It is also available in alarm
handlers for alarms scheduled on `2026-03-15` or later.

## Placement hints

Both `get(id, { locationHint })` and
`getByName(name, { locationHint })` accept a best-effort hint. It matters only
on first access and never relocates an existing object. `apac-ne` and `apac-se`
narrow the broader `apac` region. `sam`, `afr`, and `me` are accepted, but
currently fall back to a nearby region that supports Durable Objects.

```js
const stub = env.ROOMS.getByName("tokyo", { locationHint: "apac-ne" });
```
