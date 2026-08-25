---
name: phoenix-knowledge-patch
description: Phoenix
version: 1.8.x
license: MIT
metadata:
  author: Nevaberry
---


# Phoenix Knowledge Patch

Use this skill when creating, upgrading, reviewing, or debugging Phoenix
applications. Start with the quick references below, then open the topic file
that matches the work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [generators-layouts-and-projects.md](references/generators-layouts-and-projects.md) | Layout components, generator inference, generated themes and configuration, interactive project creation, Git, Docker, precommit, and usage rules |
| [runtime-apis-and-javascript.md](references/runtime-apis-and-javascript.md) | Assign APIs, channel assertions and limits, parameterized pipelines, socket reconnection, LongPoll, Presence, and transport errors |
| [scopes-and-authentication.md](references/scopes-and-authentication.md) | Generated scopes, ownership-aware contexts, route-aware scopes, authenticated LiveViews, magic links, sudo mode, and auth migration |
| [upgrades-security-and-configuration.md](references/upgrades-security-and-configuration.md) | Runtime requirements, controller and router deprecations, endpoint compile-time configuration, browser headers, LongPoll hardening, and log filtering |

## Breaking changes and upgrade hazards

### Supply controller formats

Every `use Phoenix.Controller` must declare `:formats`; use an empty list when
the controller intentionally supports none.

```elixir
use Phoenix.Controller, formats: [:html]
```

Do not carry forward the deprecated `:namespace` or `:put_default_views`
options. Name the layout module instead of using a module-less layout:

```elixir
put_layout(conn, html: {MyAppWeb.Layouts, :print})
```

Move trailing-slash URL generation away from the router's deprecated
`:trailing_slash` option and into `Phoenix.VerifiedRoutes`.

### Read endpoint compile-time settings explicitly

Code inside `Phoenix.Endpoint` cannot rely on an injected `config` variable.
Use `Application.compile_env/3`:

```elixir
@value Application.compile_env(
  :my_app,
  [MyAppWeb.Endpoint, :some_setting],
  :default
)
```

Audit settings previously supplied only at runtime; a setting needed during
endpoint compilation can otherwise cause the application to fail at boot.

### Treat layouts as function components

Keep `root.html.heex` as the single wrapper around the render pipeline. Invoke
dynamic layouts such as `app.html.heex` from templates as components instead
of configuring them as additional pipeline layouts.

```heex
<Layouts.app flash={@flash}>
  ...
</Layouts.app>
```

### Review the browser-header policy

Without an explicit Content Security Policy,
`put_secure_browser_headers` emits:

```text
base-uri 'self'; frame-ancestors 'self';
```

Configure a policy explicitly if a third-party origin must embed the
application. Do not expect `x-download-options` or `x-frame-options`; those
headers are no longer emitted by this function.

### Check runtime and transport limits

Use Erlang/OTP 25 or later. For Channels, remember that
`max_channels_per_transport` defaults to 100 as of Phoenix 1.8.9; explicitly
raise it for clients that intentionally multiplex more channels.

LongPoll is opt-in again as of Phoenix 1.8.2. Phoenix 1.8.9 also enforces a
100-event request batch limit. If a high-frequency application can exceed the
limit, move to 1.8.7 before adopting 1.8.9 and adjust the workload.

### Migrate generated authentication deliberately

Generators do not update existing authentication code. When moving from a
password-at-registration flow:

1. Add a new migration that makes `hashed_password` nullable; do not edit an
   already-used migration.
2. Set `hashed_password` to `nil` for every still-unconfirmed account to avoid
   credential pre-stuffing.
3. Account for a recently registered user losing their selected password.
   Deploy during low traffic, or introduce magic links without fully replacing
   the existing flow.

See [Scopes and Authentication](references/scopes-and-authentication.md) for
the generated magic-link flow, plug ordering, and scope setup.

## Scopes and authentication

### Pass the scope into data access

`mix phx.gen.auth Accounts User users` creates `Accounts.Scope` and normally
registers a default user scope. Generated browser and LiveView authentication
assigns it as `:current_scope`; generated contexts receive it as the first
argument and constrain queries with its owner identifier.

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

Place generated authenticated LiveView routes inside the authenticated
`live_session`. Otherwise the mount hook has not established the scope before
scoped operations run.

### Configure generator scopes completely

Define scopes under the application's `:scopes` configuration. Only one may be
the default. Supply the scope module and assign key, an `access_path` to the
owner identifier, ownership column settings, and test integration.

The fixture module must export `<name>_scope_fixture/0`, and generated tests
must be able to import the configured setup helper. Use
`schema_migration_type` when the migration type differs from `schema_type`.
Set `schema_table: nil` to generate a plain scope-id column instead of a
foreign key.

For multiple scopes, pass `--scope name`. A `route_prefix` can nest generated
routes, while `route_access_path` can expose a slug independently of the
database ownership key. Load a route-selected organization through the
existing user scope, then replace `:current_scope` in both a browser plug and a
LiveView `on_mount` hook.

### Use magic links and sudo mode

Generated authentication is magic-link-first: registration no longer asks for
a password, and password authentication is opt-in. Use `require_sudo_mode` for
sensitive operations that need recent authentication. In browser pipelines,
run `fetch_current_scope_for_user` before `require_authenticated_user`.

## Generators and project structure

### Use shorter generator invocations

The context argument is optional for `phx.gen.live`, `phx.gen.html`, and
`phx.gen.json`; it defaults from the plural resource name. `phx.gen.context`
can infer the context from the schema as well.

```console
$ mix phx.gen.live Post posts title:string
$ mix phx.new my_app --interactive
```

Use `--scope` when the resource belongs to a non-default configured scope.

### Expect generated-project side effects

When Git is available, `phx.new` initializes a repository. `--docker` produces
a Debian trixie-based setup. Generated projects also include:

- daisyUI-backed light, dark, and system themes when Tailwind is enabled;
- development support for `PORT` and HEEx `:debug_tags_location`;
- `force_ssl` enabled in `prod.exs`;
- a `mix precommit` alias;
- an `AGENTS.md` compatible with `usage_rules`; and
- a `usage_rules` directory for synchronized Phoenix guidance.

`phx.gen.auth` warns when esbuild is missing because its generated behavior
expects `phoenix_html.js` in the JavaScript bundle.

## Runtime APIs and JavaScript

### Assign maps in bulk or from existing state

`Phoenix.Socket.assign/2` accepts a function whose returned map is merged into
the current assigns. `Phoenix.Controller.assign/2` accepts the same functional
form, plus maps and keyword lists.

```elixir
socket = Phoenix.Socket.assign(socket, fn assigns ->
  %{count: assigns.count + 1}
end)

conn = Phoenix.Controller.assign(conn, current_user: user, locale: "en")
```

### Guard channel assertions

As of Phoenix 1.8.4, constrain the received payload directly in
`assert_push`, `assert_broadcast`, and `assert_reply`:

```elixir
assert_push "updated", payload when is_map(payload)
```

### Parameterize plugs in a scope

As of Phoenix 1.8.10, `Phoenix.Router.pipe_through/1` accepts configured plugs
alongside named pipelines:

```elixir
scope "/admin", MyAppWeb.Admin do
  pipe_through [:browser, {MyAppWeb.RequireRole, role: :admin}]
end
```

### Handle newer JavaScript transport behavior

The socket pauses reconnect attempts while the page is hidden. LongPoll can
fall back to `fetch()` when `XMLHttpRequest` is unavailable, can receive its
transport token in a header, and closes and retries after a batch `POST`
timeout. Transport errors are identifiable, so client code can distinguish
connection failures from unrelated socket errors.

Presence accepts a custom dispatcher for `presence_diff` broadcasts and no
longer crashes when a presence key matches a member of `Object.prototype`.

## Verification checklist

- Confirm every controller declares `:formats` and every layout names a module.
- Search endpoints for the removed injected `config` variable.
- Check CSP requirements before allowing cross-origin framing.
- Verify Channel and LongPoll workloads against their 100-item limits.
- Keep authenticated LiveViews in the session that installs the scope hook.
- Ensure route-derived scopes are loaded through an already-authorized scope.
- Confirm generated-auth assets include `phoenix_html.js`.
- Exercise hidden-tab reconnection, LongPoll timeout recovery, and transport
  error classification in JavaScript integration tests.
