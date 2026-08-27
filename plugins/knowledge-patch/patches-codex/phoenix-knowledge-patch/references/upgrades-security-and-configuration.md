# Upgrades, Security, and Configuration

Use this reference during upgrades and when reviewing endpoint configuration,
controller and router setup, browser headers, transport limits, or sensitive
parameter logging.

## Runtime requirement

Phoenix 1.8 requires Erlang/OTP 25 or later. Verify both development and
deployment runtimes before attributing compilation or boot failures to
application code.

## Controller and router deprecations

`use Phoenix.Controller` must specify `:formats`; an empty list is valid for a
controller with no formats.

```elixir
use Phoenix.Controller, formats: [:html]
```

Remove or migrate these deprecated forms:

- `use Phoenix.Controller` options `:namespace` and `:put_default_views`;
- module-less layouts; and
- the router's `:trailing_slash` option.

Name the layout module explicitly:

```elixir
put_layout(conn, html: {MyAppWeb.Layouts, :print})
```

Move trailing-slash URL generation to `Phoenix.VerifiedRoutes`.

Phoenix 1.8.6 also raises when `use Phoenix.VerifiedRoutes` appears more than
once in a module or when a list is interpolated into a verified route. Keep a
single setup call and convert list values to a supported route representation.

Tests can opt into deterministic query-parameter ordering using the top-level
Phoenix setting added in 1.8.3:

```elixir
config :phoenix, sort_verified_routes_query_params: true
```

## Endpoint compile-time configuration

The injected `config` variable is unavailable inside `Phoenix.Endpoint`. Read
compile-time values with `Application.compile_env/3`:

```elixir
@value Application.compile_env(
  :my_app,
  [MyAppWeb.Endpoint, :some_setting],
  :default
)
```

Audit endpoint settings that were previously provided only at runtime. If code
reads one during compilation, leaving it exclusively in runtime configuration
can cause a boot error after the upgrade.

## Secure browser headers

When no Content Security Policy is supplied, `put_secure_browser_headers`
sets:

```text
content-security-policy: base-uri 'self'; frame-ancestors 'self';
```

Third-party embedding therefore requires an explicit policy. The function no
longer emits the deprecated `x-download-options` or `x-frame-options` headers;
do not write checks or proxy rules that assume those defaults remain present.

## Generated production SSL configuration

Generated `prod.exs` enables `force_ssl` by default. Ensure forwarded-protocol
and trusted-proxy configuration accurately represent HTTPS, or the application
may redirect unexpectedly behind a proxy.

## LongPoll activation and request limits

Phoenix 1.8.0 unintentionally enabled LongPoll by default. Phoenix 1.8.2
restored it to opt-in, so explicitly configure the transport when it is
required.

Phoenix 1.8.6 fixes memory exhaustion caused by nd-JSON body splitting.
Phoenix 1.8.9 enforces the resulting 100-event batch limit. A high-frequency
LongPoll application that can exceed 100 events in one request should first
upgrade to Phoenix 1.8.7 before moving to 1.8.9, then adapt batching to the
enforced ceiling.

## Channels per transport

Phoenix 1.8.9 added `max_channels_per_transport` with a default of 100. Raise
it explicitly only when a client deliberately needs to multiplex more than
100 channels over one transport.

## Presence and sensitive log data

Since Phoenix 1.8.7, the default parameter filtering masks `token` in logs as
well as `password`. Preserve that protection when customizing log filters.

Phoenix 1.8.9 also prevents JavaScript Presence keys matching
`Object.prototype` members from crashing the client. Upgrade the client asset
alongside the server when relying on this hardening.
