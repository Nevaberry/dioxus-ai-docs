# RPC and WebSockets

This reference combines the capability model from the `rpc` topic with
date-gated behavior from batches `2025` and `2026`.

## RPC enablement and entrypoints

Workers RPC requires compatibility date `2024-04-03` or later, or the `rpc`
compatibility flag. Public methods on a `WorkerEntrypoint` can be invoked
through a Service Binding. Durable Object methods can be invoked through a
binding to that object. A remote call is asynchronous to its caller and must be
awaited even when the callee method is synchronous.

```ts
// Service Worker
export default class extends WorkerEntrypoint {
  add(a: number, b: number) {
    return a + b;
  }
}

// Calling Worker, with a Service Binding named MATH_SERVICE
const sum = await env.MATH_SERVICE.add(1, 2);
```

From `2025-11-17`, `ctx.exports` supplies automatically configured loopback
bindings for a Worker's top-level exports. This allows same-Worker
`WorkerEntrypoint` exports to be called without declaring explicit Service
Bindings.

## Functions and `RpcTarget` values

A function sent or returned over RPC becomes a callable stub that executes the
original function in its originating Worker. Parameters can therefore serve as
callbacks, and a returned closure can retain state.

An application-defined class must extend `RpcTarget` to cross RPC. Its methods
remain remote calls, and reading a public property requires `await`:

```ts
class Counter extends RpcTarget {
  #value = 0;
  increment() {
    return ++this.#value;
  }
  get value() {
    return this.#value;
  }
}

export default class extends WorkerEntrypoint {
  create() {
    return new Counter();
  }
}

using counter = await env.COUNTERS.create();
await counter.increment();
const value = await counter.value;
```

A plain object containing five functions creates five stubs, while an
`RpcTarget` with five methods creates one. Plain-object non-function fields are
transmitted immediately rather than fetched on demand. Instances of other
application-defined classes are rejected rather than flattened.

## Promise pipelining

RPC calls return custom thenables that also act as stubs. Omit an intermediate
`await` to pipeline a call on the eventual result with the first call in one
round trip:

```ts
using pendingCounter = env.COUNTERS.create();
await pendingCounter.increment();
```

If the first call fails, its pipelined calls fail with the same exception.

## Ownership and lifetime

### Parameter stubs

From `2026-01-20`, RPC stubs embedded in call parameters are duplicated rather
than transferred. Forwarding a parameter therefore no longer disposes the
caller's stub. A received parameter stub is still disposed when the call
returns; a callee retaining it must store `stub.dup()`. The
`rpc_params_transfer_stubs` flag restores the old transfer behavior.

### Streams, requests, and responses

RPC carries byte-oriented `ReadableStream` and `WritableStream` values as well
as `Request` and `Response`. Body flow control supports payloads larger than
the serialized-message limit. Sending transfers ownership, so clone a request
or response, or `tee()` a readable stream, before sending if the caller must
keep using it.

### Forwarding between Workers

A Worker can forward an RPC stub received from one service to another. The
recipient can call the original target through the introducing Worker without
a direct binding:

```ts
using counter = env.COUNTERS.create();
await env.CONSUMER.useCounter(counter);
```

The proxy connection exists only for the current participating execution
contexts and cannot be persisted for later use.

## Placement and size limits

RPC calls ignore Smart Placement. A Worker invoked through another Worker's
Service Binding runs locally on the caller's machine rather than at its own
configured placement.

The JSRPC serialized-message limit is 32 MiB. Use transferred streaming values
for larger payloads.

## Cross-language RPC

The cross-language guidance here derives from batch
`2026-07-30-2026-08-14`.

Python and JavaScript Workers call each other's exported methods through
ordinary Service Bindings without schemas or extra serialization code.
Structured-cloneable values cross through Pyodide's FFI, and exceptions
propagate to the caller.

```py
from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        result = await self.env.RPC.add(42, 144)
        return Response.json({"result": result})
```

When the JavaScript service exposes a named `WorkerEntrypoint`, name it on the
Python caller's binding:

```jsonc
{
  "services": [{
    "binding": "RPC",
    "service": "ts-rpc-server",
    "entrypoint": "RpcService"
  }]
}
```

In the reverse direction, call an exported Python method from JavaScript
through its normal binding, for example
`await env.PYTHON_RPC.highlight_code(code, language)`.

## WebSocket limits and errors

The maximum WebSocket message size is 32 MiB. WebSocket client failures surface
as JavaScript exceptions rather than internal errors and can be caught normally.

## Close-frame behavior

From `2026-03-03`, `WebSocket.close()` throws a `SyntaxError` `DOMException`
when the UTF-8 encoding of the reason exceeds 123 bytes. Count encoded bytes,
not JavaScript characters.

From `2026-03-10`, receiving a Close frame automatically sends the reciprocal
frame and sets `readyState` to `CLOSED` before the `close` event. Calling
`close()` from that handler is unnecessary and ignored.

A proxy that needs the old half-open phase must call
`ws.accept({ allowHalfOpen: true })`. Constructor-created WebSockets cannot use
that option; obtain the socket through an upgrade `fetch()` when half-open
handling is required.

## Binary messages

From `2026-03-17`, `WebSocket.binaryType` defaults to `"blob"`, so binary
messages arrive as `Blob` instead of `ArrayBuffer`. Set
`ws.binaryType = "arraybuffer"` before `accept()` to preserve the earlier
shape. Durable Object hibernatable WebSocket handlers continue receiving
`ArrayBuffer` regardless of the gate.
