# Python APIs, Runtime, and Dependencies

Use this reference when implementing async services, maintaining custom
interceptors or contexts, resolving protobuf constraints, or expanding the
Python runtime matrix.

## Async status aborts (`core-1.83.0`)

`grpc.aio.ServicerContext` declares `abort_with_status` in its abstract
interface. Async handlers can use the status-based abort API directly:

```python
async def handle(request, context):
    await context.abort_with_status(status)
```

Because the method is abstract-interface surface, update custom
`ServicerContext` implementations as well as handlers. Keep the call awaited,
and test that the abort terminates the RPC with the supplied status instead of
allowing later handler work to proceed.

Review fakes and test doubles too: a context that implemented only the older
abstract surface may need the new method before it can be instantiated or used
as a drop-in context.

## Custom interceptor exceptions (`core-1.83.0`)

Python `InterceptedCall` APIs handle exceptions raised by custom interceptors.
This changes the observable failure behavior of intercepted RPCs.

For each interceptor shape used by the application:

1. Raise an exception before forwarding the call.
2. Raise after any interceptor-local setup that the application performs.
3. Observe the caller-visible failure and verify cleanup.
4. Keep a successful forwarding case beside the failure case.

Cover each unary or streaming call shape that actually has a custom
interceptor; do not assume one call shape proves the behavior of all others.

## Protobuf dependency bounds (`core-1.83.0`)

There are two distinct compatibility paths:

- The main Python protobuf dependency has a lower bound of 7.35.1.
- A separate v1.83.x `grpc-status` backport has a relaxed constraint and
  remains usable with protobuf 6.x.

Do not flatten these into one repository-wide rule. First identify which gRPC
package introduces the protobuf constraint, then resolve the applicable path.
When validating a lockfile or constraints file, exercise both the main package
path and the backported `grpc-status` path if the project supports both.

## Python 3.15 support (`core-1.83.0`)

gRPC Python supports Python 3.15. Add that interpreter to the runtime matrix
when the project adopts it, and verify native packages, generated code,
interceptors, and async server behavior on the new interpreter.

Runtime support does not by itself select the correct protobuf path. Resolve
the package constraints independently from the interpreter upgrade.

## Review checklist

- Custom async contexts implement `abort_with_status`.
- Handlers await `context.abort_with_status(status)`.
- Test doubles reflect the abstract interface.
- Interceptor exceptions are tested for every call shape in use.
- Both protobuf dependency paths are represented where applicable.
- Python 3.15 is tested only with a dependency set that resolves cleanly.
