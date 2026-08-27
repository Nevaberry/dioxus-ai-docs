# Deployment and class lifecycle

## Prefer SQLite-backed namespaces

SQLite-backed Durable Objects are generally available with a 10 GB database
per object and are recommended for all new classes (2025). Create them with
`new_sqlite_classes` under legacy migrations. Only this backend exposes SQL and
point-in-time recovery. KV-backed objects remain supported, but there is no
migration path from an existing KV-backed class to SQLite.

```toml
[[migrations]]
tag = "v1"
new_sqlite_classes = ["MyDurableObject"]
```

An account that has no KV-backed Durable Object namespace cannot create its
first one through `new_classes` (2026). Such deployments must create SQLite
namespaces. Accounts with an existing KV-backed namespace may still create
more for now, and existing namespaces are unaffected.

## Declarative `exports` lifecycle

Wrangler's `exports` map is a current-state alternative to ordered, tagged
`migrations` (2026). They are mutually exclusive in one Worker. Map entries are
keyed by class name, have `type: "durable-object"`, and use lifecycle states:

- Live classes default to `created` and require `storage`.
- Tombstones can be `deleted`, `renamed`, or `transferred` and forbid `storage`.
- A receiving transfer uses `expecting-transfer` and declares storage.

Every desired or already-provisioned namespace needs a matching `exports`
entry. A class exported only from Worker code is ignored and gets no namespace;
a live entry whose class is absent from code fails deployment.

```jsonc
{
  "exports": {
    "ChatRoom": { "type": "durable-object", "storage": "sqlite" }
  }
}
```

Wrangler reports other Workers whose bindings still reference a class being
renamed or deleted. It rejects a `deleted` tombstone while the class remains in
code or any Worker in the account still binds to its namespace. Keep completed
tombstones until reconciliation lists them under `Safe to remove from exports`;
renamed and transferred tombstones remain unsafe while `referencing_scripts`
is non-empty.

## Zero-downtime rename

Use a staged alias rollout:

1. Deploy the new class and re-export it under the old name while leaving
   `exports` unchanged.
2. Keep the alias and deploy the old-name `renamed` tombstone plus the new live
   entry.
3. Remove the alias after rollout.

```ts
export class NewName extends DurableObject {}
export { NewName as OldName };
```

The rename target must be a different valid identifier, must be live in the
same map, and must not already own a namespace.

## Declarative cross-Worker transfer

Transfers are target-first and binding-last. Both Workers must belong to the
same account and dispatch-namespace context.

1. On the target, deploy `expecting-transfer` with the source name, storage,
   and `transfer_from`, but no self-referencing binding.
2. On the source, deploy `transferred` with `transferred_to`; this atomically
   commits the handoff.
3. Change the target entry to live and add its binding.
4. Remove the source binding or redirect it with `script_name`.

```jsonc
{
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

Removing or replacing the target's pending entry before the source commit
cancels the transfer without moving the namespace.

## Environments and deployment constraints

Named environments inherit top-level `exports` unless they override it. Each
environment owns separate namespaces, and its tombstones affect only that
environment.

Only `wrangler deploy` applies lifecycle changes. `wrangler versions upload`
rejects `exports`, gradual deployment is unsupported for lifecycle changes,
and rollback cannot cross a lifecycle change.

## Move from migrations to exports

Replace the entire migrations array with live entries for every active
namespace. Use `storage: "sqlite"` for classes originally created by
`new_sqlite_classes` and `storage: "legacy-kv"` for `new_classes`. This does not
move namespace data, but the transition is one-way and storage cannot later be
changed in place.

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

In the legacy flow, declare `transferred_classes` in the destination Worker's
migration and export the destination class. Do not create its namespace first;
the transfer creates it. `from`, `from_script`, and `to` can rename the class
during transfer.

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

## Keep adjacent deployments compatible

Worker and Durable Object code roll out with eventual consistency. New Worker
code can call an older Durable Object version for seconds to minutes; gradual
deployments extend that overlap. Keep RPC and request contracts forward- and
backward-compatible across adjacent releases.
