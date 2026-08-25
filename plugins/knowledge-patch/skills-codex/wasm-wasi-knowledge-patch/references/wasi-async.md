# WASI Native Async

## Native async values and functions (`wasi-0.2-guide`)

WASI native async adds three WIT constructs:

- `stream<T>` for incrementally produced ordered values;
- `future<T>` for one value delivered later; and
- `async func` for a call that may suspend.

Streams and futures are Canonical ABI values rather than resources. They may
be parameters, results, and forwarded across component boundaries. The runtime
schedules async calls, while bindings expose the host language's ordinary
async form.

```wit
interface handler {
    handle: async func(request: string) -> result<string, u32>;
    body: func() -> tuple<stream<u8>, future<result>>;
}
```

## Read data separately from completion (`wasi-0.3-guide`)

A read-like operation returns an independent data stream and terminal-result
future:

```wit
read-via-stream: func(offset: filesize)
    -> tuple<stream<u8>, future<result<_, error-code>>>;
```

The future resolves even when the caller samples or drops the stream early.
The caller therefore does not need to drain all data to learn whether the
operation succeeded. Use the same structure for stdin, TCP receives, and
directory listings.

## Reverse write data flow

Do not return a host-owned `output-stream` and then push bytes into it. The
guest passes a `stream<u8>` to the host and receives a future that completes
after the host consumes the stream.

```wit
write-via-stream: func(data: stream<u8>)
    -> future<result<_, error-code>>;
```

Stdout, stderr, filesystem writes, and TCP sends use this direction.

## Collapse two-step operations

Replace a WASI 0.2 `start-foo`/`finish-foo` pair and its intermediate
`pollable` with one operation. Make it `async func` when the host operation may
suspend, as with TCP connect. A split that existed only for nonblocking
dispatch, such as bind or listen, may become a plain `func`.

```wit
connect: async func(remote-address: ip-socket-address)
    -> result<_, error-code>;
```

## Owned async handles (`wasi-0.3.0`)

Every `stream<T>` and `future<T>` is an owned handle. Passing it over a
component boundary transfers ownership to the callee. Unlike a resource
handle, it cannot be borrowed.

## Host-wide completion scheduling

The host manages a single event loop shared by all composed components. When a
future value is delivered, the host schedules the awaiting task even if the
future crossed several component boundaries. The producer may be the host,
another component, or the same component.

This ABI is completion-based, not readiness-based. An `epoll`- or
`kqueue`-style readiness layer can be emulated for ported software that
requires one.

## Stackful and stackless bindings

The async ABI supports stackful and stackless coroutines together. Go bindings
can expose synchronous-looking functions and blocking stream operations: the
runtime parks only the goroutine that reaches the ABI boundary, then resumes
it when the stream is ready.
