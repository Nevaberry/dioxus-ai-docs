# Lifecycle, Messages, Metadata, and Schemas

## JSON-RPC batching by revision

The `2025-03-26` revision added batching, allowing multiple protocol requests
in one top-level array:

```json
[
  {"jsonrpc": "2.0", "id": 1, "method": "ping"},
  {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
]
```

The `2025-06-18` revision removes batching and reverses that addition. A
top-level array of requests or responses is no longer valid MCP. Send every
JSON-RPC message separately.

## Mandatory lifecycle operation (`2025-06-18`)

The lifecycle operation requirement is strengthened from **SHOULD** to
**MUST**. Treat the operation as required rather than optional.

## Expanded metadata interfaces (`2025-06-18`)

The schema adds `_meta` to additional interface types and defines its proper
use. Validators and generated bindings must allow metadata on the newly
covered shapes.

## Implementation descriptions (`2025-11-25`)

The `Implementation` interface includes an optional `description` field for
human-readable client or server context during initialization.

## JSON Schema dialect (`2025-11-25`)

JSON Schema 2020-12 is the default dialect for MCP schema definitions. Schema
producers, validators, and code generators should use it unless another
dialect is selected explicitly.

## Standalone request parameter schemas (`2025-11-25`)

Request payload schemas are decoupled from RPC method definitions and exposed
as standalone parameter schemas. Schema consumers and generated bindings must
account for this organization.

## Stable revision status (`2026-07-28`)

The `2026-07-28` protocol revision is stable. Behavior previously published
for that revision as release-candidate material is no longer prerelease
guidance.
