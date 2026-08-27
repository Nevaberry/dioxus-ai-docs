# Phoenix and LiveView

## Upgrade LiveView project wiring

For `liveview-1.1.0`, place the LiveView compiler before the standard Mix
compilers, add LazyHTML as a test dependency, and remove Floki only if no other
dependency or test uses it:

```elixir
# project/0
compilers: [:phoenix_live_view] ++ Mix.compilers()

# deps/0
{:phoenix_live_view, "~> 1.1"},
{:lazy_html, ">= 0.0.0", only: :test}
```

An Igniter-driven upgrade can start with:

```console
mix archive.install hex igniter_new
mix igniter.upgrade phoenix_live_view
```

Applications enabling colocated code must also update esbuild, add
`--alias:@=.`, and set `NODE_PATH` to the dependency and build paths.

## Define colocated client code

LiveView extracts a component's `<script>` at compile time in
`liveview-1.1.0`. Use `Phoenix.LiveView.ColocatedHook` for a hook and
`Phoenix.LiveView.ColocatedJS` for arbitrary JavaScript; a colocated-JS `name`
may be omitted. Colocated hooks require Phoenix 1.8 or newer.

A leading-dot hook name is module-prefixed to avoid collisions. Rename any
pre-1.1 global hook that intentionally began with `.`.

```heex
<div id="status" phx-hook=".Status"></div>
<script :type={Phoenix.LiveView.ColocatedHook} name=".Status">
  export default { mounted() { this.el.textContent = "ready" } }
</script>
```

Merge the extracted hooks into `LiveSocket`:

```javascript
import {hooks as colocatedHooks} from "phoenix-colocated/my_app"
const liveSocket = new LiveSocket("/live", Socket, {hooks: {...colocatedHooks}})
```

## Preserve collection identity

Comprehensions perform change tracking by default in `liveview-1.1.0`, using
each entry's index when no key is supplied. Add `:key` to keep stable identity
through insertions and moves:

```heex
<li :for={item <- @items} :key={item.id}>{item.name}</li>
```

Keys work on ordinary elements and components used with `:for`; they do not
work on slot entries or `:for` on slots. Prefer streams for very large
collections when retaining the collection in server memory is undesirable.

Use `stream_insert/4` with `update_only: true` to update an existing entry
without inserting it if absent:

```elixir
stream_insert(socket, :items, item, update_only: true)
```

## Render through portals

`Phoenix.Component.portal/1` renders content elsewhere in the DOM while
retaining event handling in the owning LiveView, including for LiveComponents
and nested LiveViews (`liveview-1.1.0`):

```heex
<.portal id="tooltip" target="body">
  <div role="tooltip">Saved</div>
</.portal>
```

## Preserve client-controlled state

`JS.ignore_attributes/1` prevents LiveView patches from overwriting attributes
controlled by the browser or client JavaScript (`liveview-1.1.0`):

```heex
<dialog id="modal" phx-mounted={JS.ignore_attributes(["open"])}>...</dialog>
```

Form-associated custom elements now participate in LiveView form handling like
native controls.

## Test rendered interfaces

`LiveViewTest` uses LazyHTML in `liveview-1.1.0`, supporting selectors such as
`:is()` and `:has()` and normalizing whitespace in text filters. Floki-only
`fl-contains` and `fl-icontains` selectors do not work with `element/3`; use a
text filter:

```elixir
view |> element("main a", "Sign up") |> render_click()
```

`live/3` and `live_isolated/3` raise by default when rendered DOM IDs or
LiveComponent IDs are duplicated. Their `on_error` option can alter the
behavior, but fixing duplicate IDs preserves correct patch targeting.

## Inspect and annotate LiveViews

Enable `debug_heex_annotations` from `liveview-1.0.0` to annotate rendered
markup with both component definition and caller file and line. A configured
`Phoenix.LiveReloader` can use key-click navigation to open either location:

```elixir
config :phoenix_live_view, debug_heex_annotations: true
```

In `liveview-1.1.0`, the same setting annotates slot boundaries.
`debug_attributes` additionally adds each tag's source line as `data-phx-loc`
and the LiveView PID as `data-phx-pid`:

```elixir
config :phoenix_live_view,
  debug_heex_annotations: true,
  debug_attributes: true
```

Custom `Phoenix.LiveView.TagEngine` implementations must implement the new
`annotate_slot/4` callback.

`Phoenix.LiveView.Debug` inspects running LiveViews. Its `live_components/1`
returns inspection failures as error tuples rather than raising.

## Format custom tags

`Phoenix.LiveView.HTMLFormatter` accepts `:inline_matcher` in
`liveview-1.1.0`: pass strings and regular expressions identifying custom tag
names that should be formatted as inline elements.

## Type the JavaScript client

The `liveview-1.1.0` JavaScript client ships declarations for every public API,
replacing `@types/phoenix_live_view`. Hooks can use JSDoc or subclass
`ViewHook`:

```javascript
/** @type {import("phoenix_live_view").Hook} */
const Status = { mounted() { this.pushEvent("ready", {}) } }
```

If an editor cannot find the declarations, map TypeScript `paths` to both
`node_modules/*` and `../deps/*`.

## Install Phoenix and its generator

Phoenix `phoenix-1.8.0` requires Erlang/OTP 25 or later. Existing environments
must install the matching generator archive explicitly:

```console
mix archive.install hex phx_new 1.8.0 --force
```

New applications include an `AGENTS.md` with current Phoenix and Elixir
syntax, idiom, and API guidance for coding tools.

## Understand generated frontend defaults

New `phx.new` applications in `phoenix-1.8.0` include Tailwind v4, daisyUI,
light and dark themes, and a layout theme toggle. The `phx.gen.*` generators do
not depend on daisyUI; removing it does not require rewriting generated
features.

## Use generated authentication boundaries

`mix phx.gen.auth` defaults to magic-link registration and login in
`phoenix-1.8.0`. Email/password authentication remains opt-in through user
settings. The generated `require_sudo_mode` plug protects operations that
require recent authentication.

The auth generator creates an application-owned `%MyApp.Accounts.Scope{}` and
uses it as the default scope when none exists. With that default configured,
`phx.gen.live`, `phx.gen.html`, and `phx.gen.json`:

- pass `current_scope` into context calls;
- generate scoped queries and foreign keys;
- isolate PubSub topics by scope; and
- place generated LiveView routes in the authenticated `live_session`.

Keep the scope intact across these boundaries:

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

## Call layouts explicitly

In `phoenix-1.8.0`, the root layout is unchanged, but LiveViews no longer pick
a fixed app layout through `use Phoenix.LiveView, layout: ...`. Rendered pages
call a layout function component, allowing each layout to accept its own
assigns and slots:

```heex
<Layouts.app flash={@flash}>
  <p>My LiveView page</p>
</Layouts.app>
```
