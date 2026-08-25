# Phoenix and LiveView

## LiveView source annotations (`liveview-1.0.0`)

Enable `debug_heex_annotations` in development to annotate rendered markup with
the function component's definition and the caller's file and line.
`Phoenix.LiveReloader` can use configured key-click navigation to open either
source location in the editor.

```elixir
config :phoenix_live_view, debug_heex_annotations: true
```

## LiveView upgrade wiring (`liveview-1.1.0`)

Place LiveView's compiler before the standard compilers and add LazyHTML for
tests. Remove Floki only if nothing else uses it.

```elixir
# project/0
compilers: [:phoenix_live_view] ++ Mix.compilers()

# deps/0
{:phoenix_live_view, "~> 1.1"},
{:lazy_html, ">= 0.0.0", only: :test}
```

The upgrade can be automated with:

```console
mix archive.install hex igniter_new
mix igniter.upgrade phoenix_live_view
```

Existing applications enabling colocated code must also update esbuild, add
`--alias:@=.`, and set `NODE_PATH` to the dependency and build paths.

## Colocated client code (`liveview-1.1.0`)

### Hooks and arbitrary JavaScript

LiveView extracts component `<script>` blocks at compile time. Use
`Phoenix.LiveView.ColocatedHook` for a hook and
`Phoenix.LiveView.ColocatedJS` for arbitrary JavaScript; the latter may omit
`name`. Colocated hooks require Phoenix 1.8 or newer.

A leading-dot hook name is module-prefixed to avoid global collisions. Rename
hooks that intentionally used a global leading-dot name before LiveView 1.1.

```heex
<div id="status" phx-hook=".Status"></div>
<script :type={Phoenix.LiveView.ColocatedHook} name=".Status">
  export default { mounted() { this.el.textContent = "ready" } }
</script>
```

Merge the generated hooks into the `LiveSocket` options:

```javascript
import {hooks as colocatedHooks} from "phoenix-colocated/my_app"
const liveSocket = new LiveSocket("/live", Socket, {hooks: {...colocatedHooks}})
```

### Official JavaScript types

The client ships declarations for every public API, replacing the separate
`@types/phoenix_live_view` package. Hooks can use JSDoc types or subclass
`ViewHook`. If an editor cannot resolve declarations, map TypeScript `paths` to
both `node_modules/*` and `../deps/*`.

```javascript
/** @type {import("phoenix_live_view").Hook} */
const Status = { mounted() { this.pushEvent("ready", {}) } }
```

## Rendering and change tracking (`liveview-1.1.0`)

### Keyed comprehensions

Comprehensions track changes by default, using the entry index when no key is
given. Add `:key` for stable identity through insertion and reordering. Keys work
on regular elements and components used with `:for`, but not on slot entries or
`:for` on slots. Prefer streams for very large collections when server memory
matters.

```heex
<li :for={item <- @items} :key={item.id}>{item.name}</li>
```

### Portals

`Phoenix.Component.portal/1` renders elsewhere in the DOM while keeping the
owning LiveView's event handling, including for LiveComponents and nested
LiveViews.

```heex
<.portal id="tooltip" target="body">
  <div role="tooltip">Saved</div>
</.portal>
```

### Browser-controlled attributes

`JS.ignore_attributes/1` stops LiveView patches from overwriting attributes such
as `open` that the browser or client owns.

```heex
<dialog id="modal" phx-mounted={JS.ignore_attributes(["open"])}>...</dialog>
```

### Update-only streams

Use `stream_insert/4` with `update_only: true` to update an existing item without
inserting a missing one:

```elixir
stream_insert(socket, :items, item, update_only: true)
```

### Form-associated custom elements

The client treats form-associated custom elements as inputs, so they participate
in LiveView form handling like native controls.

## LiveView testing and debugging (`liveview-1.1.0`)

### LazyHTML selectors

LiveViewTest parses HTML with LazyHTML, supporting selectors such as `:is()` and
`:has()` and normalizing whitespace in text filters. Floki-only `fl-contains` and
`fl-icontains` do not work with `element/3`; use a text filter:

```elixir
view |> element("main a", "Sign up") |> render_click()
```

### Duplicate IDs

`LiveViewTest.live/3` and `live_isolated/3` raise by default when rendered DOM or
LiveComponent IDs are duplicated. Their `on_error` option can alter this.

### Runtime inspection

`Phoenix.LiveView.Debug` inspects running LiveViews. Its `live_components/1`
returns inspection failures as error tuples instead of raising.

### Slot, tag, and PID annotations

With `debug_heex_annotations`, LiveView also annotates slot boundaries. Enable
`debug_attributes` to add source lines as `data-phx-loc` and the LiveView PID as
`data-phx-pid`. Custom `Phoenix.LiveView.TagEngine` implementations must add the
`annotate_slot/4` callback.

```elixir
config :phoenix_live_view,
  debug_heex_annotations: true,
  debug_attributes: true
```

### Custom inline formatting

`Phoenix.LiveView.HTMLFormatter` accepts `:inline_matcher`, a list of strings and
regular expressions identifying tags to format as inline elements.

## Phoenix application generation (`phoenix-1.8.0`)

### Runtime and matching generator

Phoenix 1.8 requires Erlang/OTP 25 or newer. Explicitly install the matching
generator when replacing an existing `phx.new` archive:

```console
mix archive.install hex phx_new 1.8.0 --force
```

New applications include an `AGENTS.md` with Phoenix and Elixir syntax, idiom,
and API guidance for coding tools.

### CSS and themes

New projects ship with Tailwind v4, daisyUI, light and dark themes, and a layout
theme toggle. `phx.gen.*` output does not depend on daisyUI, so removing the
plugin does not require generated feature rewrites.

### Authentication defaults

`mix phx.gen.auth` uses magic links by default for registration and login.
Standard email/password authentication remains opt-in through user settings.
Generated authentication includes `require_sudo_mode` for operations requiring
recent authentication.

### Scoped resources

`mix phx.gen.auth` creates an application-owned `%MyApp.Accounts.Scope{}` and
makes it the default scope if none exists. With a default configured,
`phx.gen.live`, `phx.gen.html`, and `phx.gen.json` thread `current_scope` through
context calls, generate scoped queries and foreign keys, and isolate PubSub by
scope. Put generated LiveView routes inside the authenticated `live_session`.

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

### Explicit app layouts

The root layout remains unchanged, but LiveViews no longer choose a fixed app
layout through `use Phoenix.LiveView, layout: ...`. Render pages through an
explicit layout function component so each layout can receive its own assigns and
slots without branching in one global layout.

```heex
<Layouts.app flash={@flash}>
  <p>My LiveView page</p>
</Layouts.app>
```
