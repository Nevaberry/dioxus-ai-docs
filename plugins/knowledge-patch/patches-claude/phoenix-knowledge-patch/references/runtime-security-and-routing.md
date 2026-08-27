# Runtime, Security, Routing, and Realtime Behavior

## Runtime and generated-application defaults

Phoenix 1.8 requires Erlang/OTP 25 or later (`1.8.x`). Tailwind-enabled new
applications use daisyUI-backed light, dark, and system themes. In development,
generated configuration honors `PORT` and enables HEEx
`:debug_tags_location`; generated `prod.exs` enables `force_ssl` by default.

Review these generated defaults when upgrading an existing project because
generators do not rewrite its configuration.

## Render layouts as function components

New applications use one `root.html.heex` around the render pipeline. Dynamic
layouts such as `app.html.heex` are regular function components invoked from
templates, not extra render-pipeline layouts:

```heex
<Layouts.app flash={@flash}>
  ...
</Layouts.app>
```

## Review secure browser headers

When callers do not provide a Content Security Policy,
`put_secure_browser_headers` now sets:

```text
content-security-policy: base-uri 'self'; frame-ancestors 'self';
```

Third-party embedding therefore requires an explicit policy. The function no
longer sets the deprecated `x-download-options` or `x-frame-options` headers.

## Update controllers, layouts, and trailing slashes

`use Phoenix.Controller` requires `:formats`; an empty list is valid. Its
`:namespace` and `:put_default_views` options are deprecated. Module-less
layouts are deprecated as well, so provide a module when setting one:

```elixir
use Phoenix.Controller, formats: [:html]
put_layout(conn, html: {MyAppWeb.Layouts, :print})
```

The router's `:trailing_slash` option is deprecated. Configure trailing-slash
URL generation through `Phoenix.VerifiedRoutes`.

## Read endpoint configuration at compile time

The injected `config` variable is no longer available inside
`Phoenix.Endpoint`. Use `Application.compile_env/3` for compile-time values:

```elixir
@value Application.compile_env(
  :my_app,
  [MyAppWeb.Endpoint, :some_setting],
  :default
)
```

Audit endpoint configuration that existed only at runtime. An application may
fail at boot after upgrading if endpoint code now reads such a value during
compilation.

## Apply parameterized plugs in router pipelines

As of `1.8.10`, `Phoenix.Router.pipe_through/1` accepts plug-and-option tuples
alongside named pipelines. This lets a scope apply a configured plug directly:

```elixir
scope "/admin", MyAppWeb.Admin do
  pipe_through [:browser, {MyAppWeb.RequireRole, role: :admin}]
end
```

## Limit channel processes per transport

Phoenix 1.8.9 adds `max_channels_per_transport`, defaulting to `100`. It bounds
the channel processes a single client can create. Raise the option explicitly
for an application that intentionally multiplexes more than 100 channels on
one transport.

## Track LongPoll activation and security changes

LongPoll behavior has several patch-level constraints:

- Phoenix 1.8.0 inadvertently enabled LongPoll by default.
- Phoenix 1.8.2 restores it to opt-in.
- Phoenix 1.8.6 fixes nd-JSON body-splitting memory exhaustion.
- Phoenix 1.8.9 enforces the resulting 100-event batch limit.

If a high-frequency LongPoll application can exceed 100 events in one request,
upgrade to 1.8.7 before moving to 1.8.9.

## Use LongPoll transport headers and timeout recovery

Phoenix Channels allows a LongPoll transport token in a header as of 1.8.10.
This mechanism is specific to the 1.8 line and is expected to change in
Phoenix 1.9.

When a LongPoll batch `POST` times out, `phoenix.js` now closes and retries the
transport rather than leaving it stalled. Transport errors emitted by
`phoenix.js` are identifiable, allowing client handling to distinguish a
connection-layer failure from other socket errors.

## Harden Presence and logging

Phoenix 1.8.9 prevents JavaScript Presence keys matching `Object.prototype`
members from crashing the client. Starting in Phoenix 1.8.7, Phoenix masks a
`token` request parameter in logs by default, alongside `password`.

## Follow stricter verified-route rules

Phoenix 1.8.6 raises in either of these cases:

- `use Phoenix.VerifiedRoutes` appears more than once in a module.
- A list is interpolated into a verified route.

Tests may opt into deterministic query-parameter ordering with the top-level
setting introduced in Phoenix 1.8.3:

```elixir
config :phoenix, sort_verified_routes_query_params: true
```
