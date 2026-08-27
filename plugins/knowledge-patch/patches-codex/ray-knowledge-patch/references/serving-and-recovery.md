# Serving and recovery

## Pipelining deployment-handle responses

A deployment method returns a `DeploymentResponse` immediately. Await it to
obtain the value, or pass it directly into another `DeploymentHandle` call.
Passing the response permits composed deployments to forward intermediate
results without materializing them locally.

```python
summary = self.summarizer.remote(text)
translation = await self.translator.translate.remote(summary)
```

## Failure-recovery boundaries

An application exception produces HTTP 500 with traceback information but does
not kill the replica. Serve replaces failed replica actors, proxies, and the
controller. After a controller restart, it restores routing policies,
deployment configuration, and other controller state from GCS.

Transient connections and internal request queues are not restored.
Whole-cluster failure requires KubeRay-level cluster recovery.

## Requests during controller failure

HTTP, gRPC, and deployment-handle requests can continue while the Serve
controller is down. Autoscaling pauses. Once the controller recovers,
autoscaling resumes without the metrics collected before the failure.

## REST management

Every Ray cluster node provides a Serve REST API server. Each server can
connect to the Serve instance and handle management requests alongside the
Serve CLI.

## Extensible request routing

The `2.56.0-2.57.0` Serve surface adds custom ingress-router interfaces and
exposes `choose_replica` and `dispatch` through deployment handles and
`AsyncioRouter`.

Router choices include experimental round-robin routing, the session-sticky
`ConsistentHashRouter`, and the token-capacity-aware
`CapacityQueueRouter`.

## HAProxy and protocol support

In Ray 2.57, from the `2.56.0-2.57.0` batch, HAProxy ingress uses the
separately distributed `ray-haproxy` package as its default binary instead
of an image-bundled build.

Direct ingress supports gRPC, including streaming, metrics, and custom request
IDs.

## Direct-ingress constraints

For `2.56.0-2.57.0`:

- `HTTPOptions.location` is deprecated; use `proxy_location`.
- A nonzero `HTTPOptions.num_cpus` raises an error.
- Direct ingress rejects an ingress deployment that also uses a custom request
  router or `serve.multiplexed`.

## Controller and request controls

The `2.56.0-2.57.0` `ControllerOptions` can configure the Serve
controller's `runtime_env`. Rolling-update percentage is configurable. The
HTTP proxy path supports per-request timeout and disconnect handling.

## LLM routing modes

For `2.56.0-2.57.0`:

- Enable direct streaming with
  `RAY_SERVE_LLM_ENABLE_DIRECT_STREAMING`.
- Select the header used for session-sticky routing with
  `RAY_SERVE_SESSION_ID_HEADER_KEY`.
- Ray 2.57 introduces experimental `KVAwareRouter` and `KVRouterActor`
  interfaces. Complete KV-cache-aware routing support is deferred to Ray 2.58.
