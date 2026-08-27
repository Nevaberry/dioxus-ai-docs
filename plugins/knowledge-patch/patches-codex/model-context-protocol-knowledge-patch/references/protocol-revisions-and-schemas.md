# Protocol Revisions and Schemas

## JSON-RPC message shape

The `2025-03-26` revision added JSON-RPC batching, allowing multiple protocol
requests in one top-level array:

```json
[
  {"jsonrpc": "2.0", "id": 1, "method": "ping"},
  {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
]
```

The `2025-06-18` revision removed JSON-RPC batching, reversing the prior
addition. A top-level array of requests or responses is no longer valid MCP;
send each JSON-RPC message separately.

## Lifecycle requirement

The `2025-06-18` revision strengthened the lifecycle operation requirement
from **SHOULD** to **MUST**. Implementations targeting that revision must treat
the operation as required rather than optional.

## Extensible metadata

The `2025-06-18` schema adds `_meta` to more interface types and defines its
proper use. Validators and generated bindings for that revision must allow
metadata on the newly covered interface shapes.

## JSON Schema dialect

JSON Schema 2020-12 is the default dialect for MCP schema definitions in
`2025-11-25`. Schema producers, validators, and code generators should use it
unless another dialect is selected explicitly.

## Standalone request parameters

In `2025-11-25`, request payload schemas are decoupled from RPC method
definitions and exposed as standalone parameter schemas. Schema consumers and
generated bindings should account for the new organization.

## Revision stability

The `2026-07-28` protocol revision is stable. Behavior previously published in
the 2026-07-28 release candidate is no longer prerelease guidance.
