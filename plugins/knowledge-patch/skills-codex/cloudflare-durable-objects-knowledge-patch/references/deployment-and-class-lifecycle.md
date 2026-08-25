# Deployment and class lifecycle

## SQLite-backed namespaces

SQLite-backed Durable Objects are generally available (since 2025). Each
object receives a 10 GB database, and new classes should use
`new_sqlite_classes`. SQL and point-in-time recovery exist only on this backend.
KV-backed objects remain supported for compatibility, but there is no migration
path that converts an existing KV-backed namespace to SQLite.

```ts
export class MyDurableObject extends DurableObject {
  sql: SqlStorage;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
  }

  sayHello() {
    return this.sql
      .exec("SELECT 'Hello, World!' AS greeting")
      .one().greeting;
  }
}
```

New KV-backed namespace creation is restricted (since 2026). An account with no
existing KV-backed Durable Object namespace cannot create one through
`new_classes`; use a SQLite-backed namespace instead. Accounts that already
have at least one KV-backed namespace may still create more for now, and
existing namespaces are unaffected.

```toml
[[migrations]]
tag = "v1"
new_sqlite_classes = ["MyDurableObject"]
```

## Declarative `exports` lifecycle

Wrangler's `exports` map is an alternative to the ordered, tagged `migrations`
array, and a Worker cannot use both forms. Entries are keyed by class name and
have `type: "durable-object"`. A class without an explicit lifecycle `state`
defaults to `created`; other states are `deleted`, `renamed`, `transferred`, and
the receiving-side `expecting-transfer`.

```jsonc
{
  "exports": {
    "ChatRoom": {
      "type": "durable-object",
      "state": "renamed",
      "renamed_to": "Room"
    },
    "Room": {
      "type": "durable-object",
      "storage": "sqlite"
    }
  }
}
```

Declarative tombstones support staged zero-downtime renames and cross-Worker
transfers. Wrangler also reports other Workers whose bindings still reference a
class being renamed or deleted. Existing Workers can continue using migrations.

## Reconciliation invariants

A class exported only from Worker code is ignored and receives no namespace.
Every desired namespace, and every already-provisioned namespace still being
managed, needs a corresponding `exports` entry. Live entries require a
`storage` value; tombstones forbid `storage`. Deployment fails when a live entry
names a class that Worker code does not export.

```jsonc
{
  "exports": {
    "ChatRoom": { "type": "durable-object", "storage": "sqlite" }
  }
}
```

## Tombstone safety gates

A `deleted` tombstone is rejected while its class remains in code or any Worker
in the account still binds to the namespace. After a lifecycle operation lands,
keep the stale tombstone until reconciliation lists it under
`Safe to remove from exports`. A renamed or transferred tombstone remains
unsafe to remove while its `referencing_scripts` list is non-empty.

## Zero-downtime rename

Perform a rename in three stages:

1. Deploy the new class while re-exporting it under the old name; leave the
   lifecycle `exports` map unchanged.
2. While retaining that alias, deploy an old-name `renamed` tombstone and a new
   live entry.
3. Remove the code alias after the second deployment finishes rolling out.

```ts
export class NewName extends DurableObject {
  // ...
}
export { NewName as OldName };
```

The rename target must be a different valid identifier, must be live in the
same map, and must not already own a namespace.

## Cross-Worker transfer with `exports`

Transfers are target-first and binding-last:

1. On the target Worker, deploy `expecting-transfer` with the source name and
   storage, but do not add a self-referencing binding.
2. On the source Worker, deploy `transferred`; this atomically commits the
   namespace handoff.
3. After rollout, change the target entry to an ordinary live entry and add its
   binding. Remove the source binding or redirect it with `script_name`.

```jsonc
{
  // Target, deployed first
  "exports": {
    "MyDO": {
      "type": "durable-object",
      "state": "expecting-transfer",
      "storage": "sqlite",
      "transfer_from": "source-worker"
    }
  }
}
```

```jsonc
{
  // Source, deployed second
  "exports": {
    "MyDO": {
      "type": "durable-object",
      "state": "transferred",
      "transferred_to": "target-worker"
    }
  }
}
```

Removing or replacing the target's pending entry before the source commits
cancels the transfer without moving the namespace. Both Workers must belong to
the same account and dispatch-namespace context.

## Environments and deployment restrictions

Named environments inherit top-level `exports` unless they override it, but
each environment owns separate namespaces and its tombstones affect only that
environment. Only `wrangler deploy` applies lifecycle changes:
`wrangler versions upload` rejects `exports`, gradual deployment is unsupported,
and rollback cannot cross a lifecycle change.

## Converting from migrations

To move to `exports`, replace the entire `migrations` array with live entries
for every active namespace. Use `sqlite` for classes created through
`new_sqlite_classes` and `legacy-kv` for classes created through `new_classes`.
No namespace data moves during this conversion. Storage cannot later change in
place, and after deploying `exports` the Worker cannot return to migrations.

```jsonc
{
  "exports": {
    "ExistingKvClass": {
      "type": "durable-object",
      "storage": "legacy-kv"
    }
  }
}
```

## Legacy cross-script transfer

In the migration-based flow, declare `transferred_classes` in the destination
Worker's migration and export the destination class. Do not pre-create the
destination namespace; the transfer creates it. The directive can rename the
class using `from`, `from_script`, and `to`.

```jsonc
{
  "migrations": [{
    "tag": "v4",
    "transferred_classes": [{
      "from": "OldClass",
      "from_script": "source-worker",
      "to": "NewClass"
    }]
  }]
}
```
