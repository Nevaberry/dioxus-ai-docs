# Uvicorn

All behavior in this reference comes from `uvicorn-release-history`.

## Runtime and lifecycle

Uvicorn 0.38 adds Python 3.14 support. Uvicorn 0.40 drops Python 3.9, so use
Python 3.10 or newer with the current release line.

Since Uvicorn 0.30.3, CLI and programmatic runs suppress `KeyboardInterrupt`.
Wrappers around `uvicorn.run()` must not depend on catching it during shutdown.

`Config.setup_event_loop()` is removed and raises from Uvicorn 0.36.1. Delete
programmatic calls rather than guarding them by platform or loop type.

## Workers and process recycling

Uvicorn 0.37 adds `--timeout-worker-healthcheck`. Uvicorn 0.41 adds
`--limit-max-requests-jitter`, which staggers restarts triggered by maximum
request counts.

The `uvicorn.workers` module is deprecated from 0.30.0. Avoid new imports from
that namespace and migrate existing worker integrations.

## Reload configuration

Uvicorn 0.33 removes WatchGod support for `--reload`. From 0.34.3, a non-empty
configured set of reload directories no longer implicitly adds the current
working directory. Declare every desired reload root explicitly.

## Protocol and loop implementations

Uvicorn 0.36 supports custom I/O loops and accepts import strings in `--http`,
`--ws`, and `--loop`. Deployments can supply implementations beyond the
built-in choices.

Uvicorn 0.32.1 advertises ASGI specification 2.3 in HTTP scopes. Code reading
`scope["asgi"]["spec_version"]` must not infer support for later HTTP features.

## Sockets, proxies, and paths

From Uvicorn 0.41, a Unix-domain socket path appears in `scope["server"]`, so
middleware can identify a socket-bound server.

From Uvicorn 0.31, `ProxyHeadersMiddleware` accepts IPv4 and IPv6 networks as
trusted hosts, supporting reverse proxies with dynamic addresses.

Since Uvicorn 0.26, the prefix supplied by `--root-path` is included in the full
ASGI `scope["path"]`. Middleware written for the former relative path must
account for the prefix.

## WebSocket disconnects

Uvicorn 0.30.2 supports `reason` on `websocket.disconnect` events. Read it
defensively because the key may be absent:

```python
event = await receive()
if event["type"] == "websocket.disconnect":
    reason = event.get("reason", "")
```

## Configuration inputs

From Uvicorn 0.30.0, `log_config` accepts a `ConfigParser` instance or an
`io.IO[Any]` stream in addition to previous forms.

Uvicorn 0.24 adds `UVICORN_APP`, allowing the application import target to come
from the environment instead of a positional CLI argument:

```console
UVICORN_APP=package.main:app uvicorn
```
