# Python APIs, Runtime, and Dependencies

Use this reference when implementing async service failures, maintaining custom
interceptors or contexts, resolving protobuf constraints, or adopting a newer
Python runtime.

All changes in this reference come from `core-1.83.0`.

## Async status aborts

`grpc.aio.ServicerContext` declares `abort_with_status` in its abstract
interface. Async handlers can abort directly with a status object:

```python
async def handle(request, context):
    await context.abort_with_status(status)
```

Apply these rules:

- Await the method; do not treat it as the synchronous context API.
- Keep custom `ServicerContext` implementations aligned with the abstract
  interface, including the status-based abort member.
- Test that handler work does not continue unexpectedly after the abort.
- Exercise the status code, details, and metadata carried by the status object
  through the application's normal error path.

## Exceptions from custom interceptors

Python `InterceptedCall` APIs now handle exceptions raised by custom
interceptors. This changes the observable failure behavior of intercepted RPCs.

The observation point can vary with the call API used by the application, so
verify the failure through that API directly:

- Raise deliberately from each custom interceptor.
- Cover every unary or streaming call shape that the interceptor wraps.
- Observe both awaiting the call and consuming responses where applicable.
- Update tests that asserted the earlier propagation or wrapping behavior only
  after recording the behavior of the upgraded package.
- Preserve causal exception information in application logging and error
  translation.

## Protobuf version bounds

The Python protobuf lower bound moves from 6.33.5 to 7.35.1. Resolve and test
that dependency change together with the gRPC Python packages in the
application's lockfile.

A separate v1.83.x backport for `grpc-status` relaxes that package's bound so it
can still be used with protobuf 6.x. Keep the two cases separate:

| Dependency path | Compatibility rule |
| --- | --- |
| Main Python protobuf requirement | Use 7.35.1 or newer |
| v1.83.x `grpc-status` backport | Protobuf 6.x remains permitted by the relaxed bound |

Before editing pins:

1. Identify which package contributes the active protobuf constraint.
2. Inspect lockfile resolution rather than assuming every gRPC-related package
   has the same lower bound.
3. Run serialization, status-details, generated-code, and import tests with the
   resolved protobuf version.
4. Avoid raising the backport's bound solely because the main dependency path
   changed.

## Python 3.15 support

gRPC Python supports Python 3.15. When adopting it:

- Add the interpreter to CI and exercise both pure-Python and native package
  installation paths used by the project.
- Regenerate or import representative protobuf modules.
- Run async server, interceptor, cancellation, and status-detail tests.
- Confirm the whole dependency graph supports the interpreter; gRPC Python
  support does not establish support for unrelated project dependencies.

## Upgrade checklist

- Implement and await `abort_with_status` in every applicable async context.
- Re-run interceptor exception tests instead of assuming the old failure shape.
- Determine whether the main protobuf bound or the `grpc-status` backport rule
  applies.
- Exercise Python 3.15 in the same packaging environment used for deployment.
