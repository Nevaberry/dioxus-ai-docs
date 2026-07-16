# Uvicorn

Use this reference when changing FastAPI server startup, workers, reload, protocols, proxy trust, ASGI scope handling, environment configuration, or embedded logging (`uvicorn-release-history`).

## Contents

- [Python support](#python-support)
- [Worker recycling and health checks](#worker-recycling-and-health-checks)
- [Protocol and event-loop implementations](#protocol-and-event-loop-implementations)
- [Reload behavior](#reload-behavior)
- [ASGI scopes](#asgi-scopes)
- [Trusted proxy networks](#trusted-proxy-networks)
- [WebSocket disconnect reasons](#websocket-disconnect-reasons)
- [Signals and programmatic runs](#signals-and-programmatic-runs)
- [Environment application target](#environment-application-target)
- [Embedded log configuration](#embedded-log-configuration)

## Python support

- Uvicorn 0.34 drops Python 3.8.
- Uvicorn 0.38 adds Python 3.14 support.
- Uvicorn 0.40 drops Python 3.9, so 0.40 and newer require Python 3.10 or later.

## Worker recycling and health checks

Uvicorn 0.37 adds `--timeout-worker-healthcheck`. Uvicorn 0.41 adds `--limit-max-requests-jitter`, allowing worker restarts to be staggered rather than occurring at one common request count:

```console
$ uvicorn app:app \
    --workers 4 \
    --limit-max-requests 10000 \
    --limit-max-requests-jitter 1000 \
    --timeout-worker-healthcheck 10
```

Use jitter in multi-worker deployments to reduce simultaneous recycling.

The `uvicorn.workers` module is deprecated as of Uvicorn 0.30. Deployment configuration and Python imports that refer to worker classes in that namespace rely on a deprecated integration point.

## Protocol and event-loop implementations

Uvicorn 0.35 adds `WebSocketsSansIOProtocol`. Uvicorn 0.36 makes custom I/O loops pluggable and accepts import strings for `--http`, `--ws`, and `--loop`:

```console
$ uvicorn app:app \
    --loop package.loops:setup \
    --http package.http:Protocol \
    --ws package.ws:Protocol
```

By Uvicorn 0.36.1, removed `Config.setup_event_loop()` explicitly raises an exception. Programmatic launchers must stop calling it; loop setup is selected through supported configuration.

## Reload behavior

Uvicorn 0.33 removes WatchGod reload support. Use the supported reload implementation and options.

Uvicorn 0.34.3 stops implicitly adding the current working directory when one or more non-empty reload directories are supplied. List every directory that should be watched:

```console
$ uvicorn app:app --reload --reload-dir src --reload-delay 0.25
```

For programmatic configuration, `reload_delay` must be numeric. Its default has been `0.25` since Uvicorn 0.18.3; `None` is not accepted.

## ASGI scopes

### HTTP spec version

Uvicorn 0.32.1 advertises ASGI spec version 2.3 on HTTP scopes. Feature-detect from the scope value rather than inferring a spec revision from the installed Uvicorn version.

### Root paths

Since Uvicorn 0.26, the `--root-path` prefix is included in the full ASGI `scope["path"]`, as required by ASGI. Middleware that combines `scope["root_path"]` with `scope["path"]` must avoid prefixing it a second time.

### Unix-domain sockets

Starting in Uvicorn 0.41, the Unix-socket path appears in `scope["server"]`. ASGI middleware inspecting this field must not assume it always contains a TCP `(host, port)` shape.

## Trusted proxy networks

Since Uvicorn 0.31, `ProxyHeadersMiddleware` accepts individual IPv4/IPv6 addresses and IP networks as trusted hosts. Configure a proxy subnet without enumerating each proxy:

```console
$ uvicorn app:app \
    --proxy-headers \
    --forwarded-allow-ips "10.0.0.0/8,2001:db8::/32"
```

When `X-Forwarded-For` is empty, Uvicorn preserves the host already present on the request rather than replacing it with an invalid empty value.

## WebSocket disconnect reasons

Uvicorn 0.30.2 adds `reason` to ASGI `websocket.disconnect` events. Use optional access when supporting older servers:

```python
message = await receive()
if message["type"] == "websocket.disconnect":
    reason = message.get("reason", "")
```

## Signals and programmatic runs

Uvicorn 0.29 introduces cooperative signal handling. Uvicorn 0.30.3 suppresses `KeyboardInterrupt` in CLI and programmatic use, so code around `uvicorn.run()` must not depend on catching that exception when the server is interrupted.

## Environment application target

Uvicorn has read configuration from environment variables since 0.16. Uvicorn 0.24 adds `UVICORN_APP` for the application import target:

```console
$ UVICORN_APP=package.main:app UVICORN_PORT=8000 uvicorn
```

## Embedded log configuration

Uvicorn 0.30 accepts a `ConfigParser` or `io.IO[Any]` object as `log_config`, so an embedded server can pass an already parsed or open logging configuration:

```python
from configparser import ConfigParser
import uvicorn

logging_config = ConfigParser()
logging_config.read("logging.ini")
uvicorn.run("package.main:app", log_config=logging_config)
```
