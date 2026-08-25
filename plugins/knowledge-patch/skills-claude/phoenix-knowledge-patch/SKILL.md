---
name: phoenix-knowledge-patch
description: Phoenix
version: 1.8.x
license: MIT
metadata:
  author: Nevaberry
---


# Phoenix Knowledge Patch

Use this skill when creating or upgrading Phoenix applications, changing
generated authentication or scopes, configuring endpoints and routers, or
working on Channels and the JavaScript client. Apply the migration and security
notes before adopting newer generator output.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Scoped Data Access and Authentication](references/scopes-and-auth.md) | Generator scopes, route-aware ownership, magic links, sudo mode, auth migration |
| [Runtime, Security, Routing, and Realtime Behavior](references/runtime-security-and-routing.md) | Runtime requirements, layouts, headers, endpoints, routers, Channels, LongPoll, Presence, logging |
| [Generators, JavaScript Clients, and Channel Tests](references/generators-client-and-testing.md) | Generator commands and side effects, assigns, guarded assertions, socket and Presence client behavior |

## Breaking Changes and Upgrade Hazards

### Meet the runtime requirement

Phoenix 1.8 requires Erlang/OTP 25 or later. Check production, CI, and local
runtime versions before upgrading dependencies.

### Make controller formats explicit

Every `use Phoenix.Controller` must now provide `:formats`; use an empty list
when the controller intentionally has no formats.

```elixir
use Phoenix.Controller, formats: [:html]
```

Replace deprecated controller options `:namespace` and `:put_default_views`.
Module-less layouts are also deprecated, so identify the layout module:

```elixir
put_layout(conn, html: {MyAppWeb.Layouts, :print})
```

The router's `:trailing_slash` option is deprecated. Move trailing-slash URL
generation to `Phoenix.VerifiedRoutes`.

### Read endpoint compile-time settings explicitly

The injected `config` variable is unavailable inside `Phoenix.Endpoint`.
Read compile-time endpoint settings with `Application.compile_env/3`:

```elixir
@value Application.compile_env(
  :my_app,
  [MyAppWeb.Endpoint, :some_setting],
  :default
)
```

Audit settings supplied only at runtime; code that now expects them at compile
time can otherwise fail while booting after an upgrade.

### Treat layouts as components

New applications keep a single `root.html.heex` around the render pipeline.
Invoke dynamic layouts such as the application layout from templates as
function components:

```heex
<Layouts.app flash={@flash}>
  ...
</Layouts.app>
```

### Review browser embedding policy

Without an explicit Content Security Policy, `put_secure_browser_headers`
sets `content-security-policy` to `base-uri 'self'; frame-ancestors 'self';`.
Define an explicit policy when third parties must embed the application. The
function no longer emits the deprecated `x-download-options` or
`x-frame-options` headers.

### Migrate generated authentication deliberately

Generators do not retrofit existing authentication code. To migrate an older
password-registration flow, add a new migration that makes
`hashed_password` nullable; do not edit an already-run migration. Set the
field to `nil` for all still-unconfirmed accounts to prevent credential
pre-stuffing.

That cleanup can invalidate a password chosen moments before deployment. Run
it during low traffic, or add magic-link login without immediately replacing
the existing password flow. See the authentication reference for the complete
generated flow.

### Account for LongPoll security and limits

LongPoll is opt-in from Phoenix 1.8.2 onward. Phoenix 1.8.6 fixes nd-JSON
body-splitting memory exhaustion, and Phoenix 1.8.9 enforces a 100-event batch
limit. A high-frequency application that can exceed that limit should upgrade
to 1.8.7 before moving to 1.8.9. See the runtime reference for transport
recovery and token behavior.

### Respect verified-route strictness

Phoenix 1.8.6 raises if `use Phoenix.VerifiedRoutes` occurs more than once in
a module or if a list is interpolated into a verified route. Remove duplicate
uses and construct query data without list interpolation.

For stable test output, enable deterministic query-parameter sorting:

```elixir
config :phoenix, sort_verified_routes_query_params: true
```

## Scoped Generation

### Pass scopes through context boundaries

`mix phx.gen.auth Accounts User users` generates `Accounts.Scope` and normally
registers a default user scope. Browser requests receive `:current_scope`
through `fetch_current_scope_for_user`, and generated LiveViews receive it
through a mount hook.

Once a default is configured, schema, context, LiveView, HTML, and JSON
generators produce ownership fields and scoped queries. Keep the scope as the
first argument to context operations:

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

Place generated authenticated LiveView routes in the authenticated
`live_session`; otherwise the scope is not mounted before scoped operations.

### Configure the ownership and route identities separately

A scope declaration controls its assign, owner lookup, schema association,
fixtures, and generated test setup. Only one configured scope may be the
default. Select another with `--scope`.

For nested routes, `route_prefix` and `route_access_path` can expose a slug
while `access_path` and `schema_key` retain an internal database identifier.
Load a route-selected organization through the existing user scope, then
replace `:current_scope` in both the browser plug and LiveView `on_mount`
hook. The scopes reference contains complete configurations and edge cases.

## Authentication Quick Reference

Phoenix 1.8 generated authentication is magic-link-first. Registration no
longer collects a password, and password authentication is opt-in. Generated
`UserAuth` includes `require_sudo_mode` for sensitive actions that demand
recent authentication.

In browser pipelines, `require_authenticated_user` must run after
`fetch_current_scope_for_user`. Also keep `phoenix_html.js` in the JavaScript
bundle; `phx.gen.auth` warns if esbuild is unavailable because generated
features assume that asset is present.

## Routing and Realtime Quick Reference

### Parameterize plugs in a scope

`Phoenix.Router.pipe_through/1` accepts plug-and-options tuples alongside named
pipelines:

```elixir
scope "/admin", MyAppWeb.Admin do
  pipe_through [:browser, {MyAppWeb.RequireRole, role: :admin}]
end
```

### Bound channels per transport

Phoenix 1.8.9 defaults `max_channels_per_transport` to `100`. Raise it
explicitly only for clients intentionally multiplexing more than 100 channel
processes over one transport.

### Handle LongPoll and transport failures

LongPoll transport tokens may be sent in a header. This 1.8-line mechanism is
expected to change in Phoenix 1.9. When a LongPoll batch `POST` times out,
`phoenix.js` closes and retries the transport instead of leaving it stalled.
JavaScript transport errors are identifiable, so client handlers can separate
connection-layer failures from other socket errors.

## Common New APIs

### Bulk and functional assigns

`Phoenix.Socket.assign/2` accepts a function of current assigns and merges the
returned map. `Phoenix.Controller.assign/2` accepts that form, maps, and keyword
lists.

```elixir
socket = Phoenix.Socket.assign(socket, fn assigns ->
  %{count: assigns.count + 1}
end)

conn = Phoenix.Controller.assign(conn, current_user: user, locale: "en")
```

### Guard channel assertions

`assert_push`, `assert_broadcast`, and `assert_reply` accept guards, allowing
payload constraints in the receive assertion:

```elixir
assert_push "updated", payload when is_map(payload)
```

### Use streamlined generators

The context argument for `phx.gen.live`, `phx.gen.html`, and `phx.gen.json` is
optional and defaults from the plural name. `phx.gen.context` can infer its
context from the schema, and `phx.new` offers interactive setup.

```console
$ mix phx.gen.live Post posts title:string
$ mix phx.new my_app --interactive
```

Open the generator reference before scripting these commands because new
projects also create or select additional tooling and repository files.
