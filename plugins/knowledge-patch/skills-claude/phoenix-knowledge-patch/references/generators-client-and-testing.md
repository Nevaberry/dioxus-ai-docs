# Generators, JavaScript Clients, and Channel Tests

## Use bulk and functional assigns

`Phoenix.Socket.assign/2` can take a function of the current assigns; the map
returned by that function is merged into the assigns (`1.8.x`).

```elixir
socket = Phoenix.Socket.assign(socket, fn assigns ->
  %{count: assigns.count + 1}
end)
```

`Phoenix.Controller.assign/2` now accepts the same functional form as well as
maps and keyword lists, matching the bulk-assignment style used by LiveView:

```elixir
conn = Phoenix.Controller.assign(conn, current_user: user, locale: "en")
```

## Put guards in channel assertions

Since Phoenix 1.8.4, `assert_push`, `assert_broadcast`, and `assert_reply`
support guards. Constrain a received payload without a separate assertion:

```elixir
assert_push "updated", payload when is_map(payload)
```

## Use inferred generator contexts

The context argument is optional for `phx.gen.live`, `phx.gen.html`, and
`phx.gen.json`; each defaults it from the plural name. `phx.gen.context` can
similarly infer a context from the schema.

```console
$ mix phx.gen.live Post posts title:string
```

`phx.new` also has an interactive mode:

```console
$ mix phx.new my_app --interactive
```

## Preserve authentication JavaScript assets

`phx.gen.auth` warns if esbuild is unavailable because its generated features
assume `phoenix_html.js` is present in the JavaScript bundle. If the project
uses another asset pipeline, ensure it still includes the module.

## Expect new-project side effects and tooling

When Git is installed, `phx.new` initializes a repository. The `--docker`
option now selects Debian trixie as its base image.

Generated projects also contain:

- A `mix precommit` alias.
- An `AGENTS.md` compatible with `usage_rules`.
- A `usage_rules` directory for synchronizing Phoenix guidance.

Account for these files and the automatic repository initialization when
wrapping `phx.new` in scripts or applying a project template.

## Handle JavaScript socket visibility and fallback transport

The JavaScript socket stops reconnect attempts while the page is hidden. Code
that reports connection state should account for reconnection resuming after
the page becomes visible.

LongPoll can use `fetch()` when `XMLHttpRequest` is unavailable. Do not assume
that observing or instrumenting `XMLHttpRequest` captures every LongPoll
request.

## Customize Presence dispatch

JavaScript Presence supports a custom dispatcher for `presence_diff`
broadcasts. Use it when an application needs to schedule or route diff
processing instead of applying every broadcast through the default dispatch
path.
