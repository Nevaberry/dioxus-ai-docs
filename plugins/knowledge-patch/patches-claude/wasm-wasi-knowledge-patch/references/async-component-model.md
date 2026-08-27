# Async Component Model

Use this reference when designing asynchronous WIT interfaces, transferring
async values between components, or defining HTTP service roles. It includes
guidance from `wasi-0.2-guide` and `wasi-0.3.0`.

## Native async values and functions

WASI 0.3 adds three native forms:

- `stream<T>` represents incrementally produced ordered values.
- `future<T>` represents one value delivered later.
- `async func` represents a call that may suspend.

Streams and futures are Canonical ABI values rather than resources. They can
be parameters, results, and values forwarded across component boundaries. The
runtime schedules async calls, while bindings expose the host language's normal
async form.

```wit
interface handler {
    handle: async func(request: string) -> result<string, u32>;
    body: func() -> tuple<stream<u8>, future<result>>;
}
```

## Stable compatibility within the 0.3 line

WASI 0.3.0 is a ratified stable release. Components compiled for it are
guaranteed to continue working as later 0.3.x patch releases ship.

## Async handle ownership

Every `stream<T>` and `future<T>` behaves as an owned handle. Passing one across
a component boundary transfers ownership to the callee. Unlike a resource
handle, a stream or future cannot be borrowed.

## Host-wide completion scheduling

The host manages one event loop shared by all composed components. Delivering
a future value schedules its awaiting task even after the future crosses
multiple component boundaries. The producer can be the host, a different
component, or the same component.

The ABI is completion-based rather than readiness-based. When porting software
that requires readiness notifications, an `epoll`- or `kqueue`-style layer can
be emulated on top.

## Stackful and stackless bindings

The async ABI supports stackful and stackless coroutines together. Go bindings
can expose synchronous-looking functions and blocking stream operations: the
runtime parks only the calling goroutine at the ABI boundary and resumes it
when the stream is ready.

## HTTP service and middleware roles

The `service` world imports the HTTP `client` and exports the incoming
`handler`. The `middleware` world includes `service` and also imports a
downstream `handler`, making it the successor to the 0.2 `proxy` world.

```wit
world service {
    import client;
    export handler;
}

world middleware {
    include service;
    import handler;
}
```
