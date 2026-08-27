# Python APIs, Runtime, and Dependencies

## Abort asynchronous RPCs with a status object

`grpc.aio.ServicerContext` declares `abort_with_status` in its abstract
interface. Async handlers can await the status-based abort API directly:

```python
async def handle(request, context):
    await context.abort_with_status(status)
```

Update custom `ServicerContext` implementations to satisfy the abstract
interface. Test that awaiting the method terminates handler control flow with
the intended status, including through wrappers or test doubles that implement
the context themselves.

## Custom interceptor exceptions

Python `InterceptedCall` APIs handle exceptions raised by custom interceptors.
This changes the observable failure behavior of intercepted RPCs, so do not keep
tests or application logic that depend on the earlier handling path.

Raise representative exceptions from each custom interceptor shape the
application uses. Verify the resulting call failure, status, cleanup, and any
application-level translation for unary and streaming RPC shapes in scope.

## Protobuf dependency bounds

The main Python protobuf dependency moves its lower bound from 6.33.5 to
7.35.1. Resolve that path independently from the v1.83.x `grpc-status`
backport: its relaxed bound allows continued use with protobuf 6.x.

Before editing a requirement or lockfile:

1. Identify whether the constraint comes from the main gRPC package or the
   `grpc-status` backport.
2. Apply the 7.35.1 lower bound only to the main dependency path.
3. Preserve protobuf 6.x compatibility where the backport is intentionally in
   use.
4. Resolve and test both environments if the project distributes artifacts for
   both dependency paths.

## Python 3.15 support

gRPC Python supports Python 3.15. Add that interpreter to the supported-runtime
matrix when the application adopts it, and verify installation, generated-code
imports, async RPCs, interceptor failures, and native dependency availability
under the same constraints used for released artifacts.
