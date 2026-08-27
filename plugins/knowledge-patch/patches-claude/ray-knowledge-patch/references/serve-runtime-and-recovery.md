# Ray Serve Runtime and Recovery

## Pipeline deployment-handle responses

A deployment method returns a `DeploymentResponse` immediately. Await it for
its value, or pass it directly to another `DeploymentHandle` call to forward an
intermediate result without materializing it locally.

```python
summary = self.summarizer.remote(text)
translation = await self.translator.translate.remote(summary)
```

## Understand failure-recovery boundaries

An application exception produces HTTP 500 with traceback information without
killing the replica. Serve replaces failed replica actors and restarts failed
proxies and the controller. The controller restores routing policies and
deployment configuration from the GCS.

Transient connections and internal request queues are lost. Recovering from an
entire cluster failure requires KubeRay-level cluster recovery.

## Serve while the controller is unavailable

HTTP, gRPC, and deployment-handle requests can continue while the Serve
controller is down. Autoscaling pauses. After recovery it resumes without the
metrics generated during the outage.

## Use per-node REST management

Every Ray cluster node exposes a Serve REST API server that can connect to the
Serve instance and process management requests. The Serve CLI remains available
alongside these servers.

## Extend request routing

The routing changes grouped in `2.56.0-2.57.0` add custom ingress-router
interfaces and expose `choose_replica` and `dispatch` through deployment handles
and `AsyncioRouter`.

Router choices include experimental round-robin routing,
session-sticky `ConsistentHashRouter`, and token-capacity-aware
`CapacityQueueRouter`.

## Package HAProxy and use direct-ingress protocols

In Ray 2.57, HAProxy ingress uses the separately distributed `ray-haproxy`
package as its default binary instead of an image-bundled build. Direct ingress
supports gRPC, including streaming, metrics, and custom request IDs.

## Check direct-ingress compatibility

- `HTTPOptions.location` is deprecated; use `proxy_location`.
- A nonzero `HTTPOptions.num_cpus` raises an error.
- Direct ingress rejects an ingress deployment that also has a custom request
  router or uses `serve.multiplexed`.

## Configure the controller and requests

`ControllerOptions` can set the Serve controller's `runtime_env`. Rolling-update
percentage is configurable. The HTTP proxy path handles per-request timeouts and
client disconnects.

## Select LLM routing behavior

- Set `RAY_SERVE_LLM_ENABLE_DIRECT_STREAMING` to enable direct streaming.
- Set `RAY_SERVE_SESSION_ID_HEADER_KEY` to choose the header used for
  session-sticky routing.
- Ray 2.57 introduces experimental `KVAwareRouter` and `KVRouterActor`
  interfaces. Complete KV-cache-aware routing is deferred to 2.58.
