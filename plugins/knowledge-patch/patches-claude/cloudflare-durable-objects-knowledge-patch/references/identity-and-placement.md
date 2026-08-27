# Identity and placement

## Read a named object's identity

An object reached through `idFromName()` or `getByName()` can read that name
through `ctx.id.name`, including in an alarm handler (2026). The value is
`undefined` for IDs from `newUniqueId()`, access through `idFromString()`, and
names longer than 1,024 bytes.

```js
export class ChatRoom extends DurableObject {
  getRoomName() {
    return this.ctx.id.name;
  }
}
```

## Scope a namespace to a jurisdiction

`namespace.jurisdiction("us")` constrains an object's compute and stored data
to the United States (2026); Workers outside the US can still access it.
Jurisdiction scopes also include `eu` and `fedramp`.

```js
const usObjects = env.MY_DURABLE_OBJECT.jurisdiction("us");
const stub = usObjects.getByName("general");
```

Each jurisdiction has a distinct ID space: the same name yields a different ID
per scope, and a scoped namespace rejects an ID from another jurisdiction. An
unscoped namespace can resolve a restricted ID. Prefer scoping the namespace
over calling `newUniqueId({ jurisdiction })`; a `DurableObjectId` may still be
logged outside its jurisdiction for billing and debugging.

## Preserve jurisdiction through ID round-trips

Inside an object, `ctx.id.jurisdiction` reports its jurisdiction. The value
survives `toString()` and `idFromString()`. It is available in alarm handlers
for alarms scheduled on `2026-03-15` or later.

```js
export class Room extends DurableObject {
  getJurisdiction() {
    return this.ctx.id.jurisdiction;
  }
}
```

## Use placement hints only for first access

Both `get(id, { locationHint })` and `getByName(name, { locationHint })` accept
a best-effort hint for the object's first access. A hint never relocates an
existing object.

`apac-ne` and `apac-se` narrow the broader `apac` region. `sam`, `afr`, and
`me` are accepted but currently place objects in a nearby region with Durable
Objects support.

```js
const stub = env.ROOMS.getByName("tokyo", { locationHint: "apac-ne" });
```
