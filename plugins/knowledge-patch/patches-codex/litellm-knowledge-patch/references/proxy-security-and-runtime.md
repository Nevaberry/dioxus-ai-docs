# Proxy Security and Runtime Controls

## Input and network validation

### SSRF validation for user-controlled URLs

`litellm_settings.user_url_validation` defaults to `true`. It blocks fetched
URLs whose DNS result is private, loopback, link-local, or otherwise
non-global. `user_url_allowed_hosts` entries must exactly match the hostname
in the URL and include its port when one is present. For split-horizon DNS,
allowlist the public hostname rather than the resolved private address.

### Opt-in request and upload validation

`enable_json_schema_validation` validates every request.
`enable_key_alias_format_validation` requires aliases to contain 2–255
characters, start and end with an alphanumeric character, and otherwise use
only `a-zA-Z0-9_-/.@`.

With `require_managed_files: true`, `POST /v1/files` requires
`target_model_names` and rejects classic provider uploads with status 400.

### Request-parameter checks across input locations

Since 1.97.0, request-parameter checks apply uniformly to request bodies, path
parameters, and form inputs. This is breaking: a request that formerly evaded
a check through one of those locations can now be rejected.

## Request lifecycle

### Graceful drain and client-disconnect handling

`enable_drain_endpoint` exposes `GET /health/drain` for pre-stop hooks and is
off by default. Without `drain_endpoint_token`, the endpoint is
unauthenticated. When a token is configured, callers must send the same value
in `X-Drain-Token`.

`cancel_on_disconnect: true` cancels a non-streaming upstream request when its
client disconnects and records the cancellation as status 499.

### Request and pass-through bounds

`max_request_size_mb` rejects an oversized request, while
`max_response_size_mb` prevents an oversized model response from being sent.
`pass_through_request_timeout` separately limits custom and native-provider
pass-through requests and defaults to 600 seconds. An endpoint-specific
timeout takes precedence.

## Deployment hardening

### Deployment hardening switches

`LITELLM_ENABLE_HSTS` opts into HSTS, which applies only when the proxy is
served over HTTPS. `DISABLE_ADMIN_UI`, `NO_DOCS`, `NO_OPENAPI`, and `NO_REDOC`
independently remove exposed interfaces.

Log secret redaction is enabled unless
`LITELLM_DISABLE_REDACT_SECRETS=true`. File-backed OIDC credentials are
restricted by `LITELLM_OIDC_ALLOWED_CREDENTIAL_DIRS`; the default allowed
directories are `/var/run/secrets,/run/secrets`.
