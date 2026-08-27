# Runtime APIs and JavaScript Behavior

Use this reference for controller and socket assigns, channel tests and
resource limits, router pipelines, Presence, LongPoll, and client transport
behavior.

## Bulk and functional assigns

`Phoenix.Socket.assign/2` accepts a function of the existing assigns. The
function must return a map, which Phoenix merges into the current assigns.

```elixir
socket = Phoenix.Socket.assign(socket, fn assigns ->
  %{count: assigns.count + 1}
end)
```

`Phoenix.Controller.assign/2` accepts the same functional form, as well as a
map or keyword list:

```elixir
conn = Phoenix.Controller.assign(conn, current_user: user, locale: "en")
```

Use the functional form when the new values depend on the current assigns and
the bulk forms when several independent values belong in one update.

## Guarded channel assertions

Since Phoenix 1.8.4, `assert_push`, `assert_broadcast`, and `assert_reply`
accept guards. Constrain a received payload directly instead of adding a
separate assertion:

```elixir
assert_push "updated", payload when is_map(payload)
```

## Channel processes per transport

Phoenix 1.8.9 introduced `max_channels_per_transport`, which defaults to 100.
It bounds the number of channel processes that one client can create over a
transport.

Applications that intentionally multiplex more than 100 channels for a single
client must raise this option explicitly. Otherwise, treat the limit as a
resource-safety boundary rather than working around it in client code.

## Parameterized plugs in router pipelines

Since `1.8.10`, `Phoenix.Router.pipe_through/1` accepts plug-and-option tuples
alongside named pipelines. A scope can therefore apply a configured plug
directly:

```elixir
scope "/admin", MyAppWeb.Admin do
  pipe_through [:browser, {MyAppWeb.RequireRole, role: :admin}]
end
```

## Verified-route strictness and deterministic tests

Phoenix 1.8.6 raises if `use Phoenix.VerifiedRoutes` appears more than once in
the same module. It also raises when a list is interpolated into a verified
route. Refactor repeated setup to one `use` and serialize route values rather
than interpolating lists.

For deterministic query-parameter ordering in tests, enable the top-level
setting introduced in Phoenix 1.8.3:

```elixir
config :phoenix, sort_verified_routes_query_params: true
```

Keep this setting test-focused when production behavior does not require
ordered query serialization.

## Socket reconnection and LongPoll fallback

The JavaScript socket stops reconnect attempts while the page is hidden. Test
reconnection behavior across `visibilitychange` transitions rather than
expecting background retry timers to continue.

LongPoll can use `fetch()` when `XMLHttpRequest` is unavailable. This permits a
client environment without XHR, but does not make LongPoll active by default;
the transport remains opt-in as of Phoenix 1.8.2.

## LongPoll transport tokens

Since Phoenix 1.8.10, a Phoenix Channels LongPoll transport token may be sent
in a header. This mechanism is specific to the 1.8 line and is expected to
change in Phoenix 1.9, so isolate header construction in client integration
code rather than treating it as a permanent transport contract.

## LongPoll timeout recovery

When a LongPoll batch `POST` times out, `phoenix.js` closes and retries the
transport. Client monitoring should expect a replacement connection rather
than a permanently stalled transport.

## Identifiable transport errors

Transport errors produced by `phoenix.js` are identifiable as of Phoenix
1.8.10. Use that identity to distinguish connection-layer failures from other
socket errors instead of parsing error text.

## Presence dispatch and key safety

Presence supports a custom dispatcher for `presence_diff` broadcasts. Use it
when application-specific scheduling or delivery behavior is needed for
presence updates.

Phoenix 1.8.9 prevents presence keys matching `Object.prototype` members from
crashing the JavaScript client. Do not reintroduce unsafe plain-object lookup
logic when wrapping Presence or processing its state.
