# Uvicorn

## Runtime support

Uvicorn 0.38 adds Python 3.14 support. Uvicorn 0.40 drops Python 3.9, so the
current release line requires Python 3.10 or newer.

## Worker health and staggered restarts

Uvicorn 0.37 adds `--timeout-worker-healthcheck`. Uvicorn 0.41 adds
`--limit-max-requests-jitter`, which staggers worker restarts triggered by
maximum-request limits and reduces simultaneous recycling.

## Pluggable protocols and loops

Uvicorn 0.36 supports custom I/O loops and accepts importable strings in
`--http`, `--ws`, and `--loop`. Deployments can supply implementations beyond
the built-in choices.

`Config.setup_event_loop()` was removed. Calling it raises an exception from
Uvicorn 0.36.1; programmatic startup code must stop invoking it.

## Declare every reload root

Uvicorn 0.33 removes WatchGod support for `--reload`. From Uvicorn 0.34.3, a
non-empty configured set of reload directories no longer implicitly includes
the current working directory. Declare every directory that should trigger a
reload.

## ASGI scope changes

Uvicorn 0.32.1 advertises ASGI spec version 2.3 in HTTP scopes. Code inspecting
`scope["asgi"]["spec_version"]` must not infer support for later HTTP features.

From Uvicorn 0.41, the path of a Unix-domain socket appears in
`scope["server"]`, allowing applications and middleware to identify a
socket-bound server.

Since Uvicorn 0.26, the prefix supplied with `--root-path` is included in the
complete `scope["path"]`. Middleware written for the previous relative path
must account for the prefix.

## Trust proxy networks

From Uvicorn 0.31, `ProxyHeadersMiddleware` accepts IPv4 and IPv6 networks as
trusted hosts. Use network ranges when reverse proxies have dynamic addresses,
and keep the ranges no broader than the deployment requires.

## Shutdown and WebSocket events

Since Uvicorn 0.30.3, both CLI and programmatic runs suppress
`KeyboardInterrupt`. Wrappers around `uvicorn.run()` should not depend on
catching that exception during shutdown.

Uvicorn 0.30.2 supports the `reason` field on `websocket.disconnect` events.
Read it defensively because senders may omit it:

```python
event = await receive()
if event["type"] == "websocket.disconnect":
    reason = event.get("reason", "")
```

## Worker imports

The `uvicorn.workers` module is deprecated from Uvicorn 0.30.0. Avoid new
integrations that import worker classes from it and migrate existing imports.

## Log configuration inputs

From Uvicorn 0.30.0, `log_config` accepts a `ConfigParser` instance or an
`io.IO[Any]` stream in addition to existing configuration forms. Programmatic
launchers can pass an already parsed configuration or open stream directly.

## Configure the application target through the environment

Uvicorn 0.24 adds `UVICORN_APP`, allowing the import target to be configured
without a positional command-line argument:

```console
UVICORN_APP=package.main:app uvicorn
```
