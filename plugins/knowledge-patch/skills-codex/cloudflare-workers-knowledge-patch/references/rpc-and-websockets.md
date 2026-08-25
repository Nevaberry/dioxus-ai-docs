# RPC and WebSockets

Use this reference for Service Binding or Durable Object RPC, capability
lifetime and ownership, cross-language calls, and WebSocket compatibility.

Relevant source batches: `2025`, `2026`, `rpc`, and
`2026-07-30-2026-08-14`.

## Enable RPC and define entrypoints

Workers RPC requires compatibility date `2024-04-03` or later, or the `rpc`
compatibility flag. Public methods on a `WorkerEntrypoint` can be invoked
through a Service Binding. Durable Object public methods can be called through
that object's binding.

Even a synchronous callee method is asynchronous to its caller:

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

From compatibility date `2025-11-17`, `ctx.exports` supplies automatically
configured loopback bindings for top-level exports. A Worker can call its own
`WorkerEntrypoint` exports without declaring explicit service bindings.

## Functions and `RpcTarget` objects are capabilities

A function sent or returned over RPC becomes a callable stub. Invoking it runs
the original function in its originating Worker, enabling callback parameters
and stateful returned closures.

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

A plain object with five functions creates five stubs. An `RpcTarget` with five
methods creates one stub. Plain-object non-function fields transmit immediately
rather than being fetched on demand. Instances of other application classes
are rejected rather than flattened into plain objects.

Use explicit disposal such as `using` where supported to release capability
stubs promptly.

## Promise pipelining

RPC calls return custom thenables that also act as stubs. Calling a method on an
unresolved RPC result lets the calls travel in one round trip:

```ts
using pendingCounter = env.COUNTERS.create();
await pendingCounter.increment();
```

If creation fails, the pipelined calls fail with the same exception. Insert an
intermediate `await` only when the resolved value is actually needed locally.

## Stub ownership in parameters

From compatibility date `2026-01-20`, a stub embedded in RPC parameters is
duplicated rather than transferred. Forwarding a parameter no longer disposes
the caller's stub implicitly.

The callee's received parameter stub is still disposed when the call returns.
If the callee must keep it, store `stub.dup()` rather than the received stub.
Use `rpc_params_transfer_stubs` only to restore the earlier transfer behavior.

## Streams and large values

The serialized JSRPC message limit is 32 MiB. RPC can carry byte-oriented
`ReadableStream` and `WritableStream` values, plus `Request` and `Response`,
with body flow control suitable for larger payloads.

Sending one of these values transfers ownership. Clone a `Request` or
`Response`, or `tee()` a readable stream, before the call if the sender must
retain a usable copy.

## Forwarding stubs

A Worker can pass a stub received from one service to a different service. The
recipient can then call the original target through the introducing Worker even
without a direct binding:

```ts
using counter = env.COUNTERS.create();
await env.CONSUMER.useCounter(counter);
```

The proxy connection lasts only for the current execution contexts and cannot
be persisted for later use.

## Placement

Smart Placement does not apply to RPC. A Worker invoked through another
Worker's Service Binding runs locally on the caller's machine rather than at
the placement configured for the target.

## Cross-language Workers RPC

Python and JavaScript Workers can call each other's exported methods through
ordinary Service bindings. Structured-cloneable values cross through Pyodide's
FFI, and exceptions propagate to the caller. No schema or extra serialization
layer is required.

```py
from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        result = await self.env.RPC.add(42, 144)
        return Response.json({"result": result})
```

When the JavaScript service exports a named `WorkerEntrypoint`, select that
entrypoint in the Python caller's binding:

```jsonc
{
  "services": [{
    "binding": "RPC",
    "service": "ts-rpc-server",
    "entrypoint": "RpcService"
  }]
}
```

In the opposite direction, JavaScript calls an exported Python method normally,
for example `await env.PYTHON_RPC.highlight_code(code, language)`.

## WebSocket limits and failures

The maximum WebSocket message size is 32 MiB. WebSocket client failures surface
as JavaScript exceptions rather than internal errors, so catch them through
normal exception handling.

## Close-reason validation

From compatibility date `2026-03-03`, `WebSocket.close()` throws a
`SyntaxError` `DOMException` when the UTF-8 encoding of its reason exceeds 123
bytes. Validate encoded bytes, not JavaScript character count.

## Automatic close replies and half-open proxies

From `2026-03-10`, receiving a Close frame automatically sends the reciprocal
frame and sets `readyState` to `CLOSED` before dispatching `close`. Calling
`close()` inside that handler is unnecessary and ignored.

For a proxy that needs the older half-open phase, use:

```ts
ws.accept({ allowHalfOpen: true });
```

Constructor-created WebSockets cannot use this option. Obtain the WebSocket
through an upgrade `fetch()` when half-open handling is required.

## Standard binary type

From `2026-03-17`, `WebSocket.binaryType` defaults to `"blob"`, so binary
messages arrive as `Blob`. To keep `ArrayBuffer`, set the type before accepting:

```ts
ws.binaryType = "arraybuffer";
ws.accept();
```

Durable Object hibernatable WebSocket handlers continue to receive
`ArrayBuffer` regardless of this compatibility gate.
