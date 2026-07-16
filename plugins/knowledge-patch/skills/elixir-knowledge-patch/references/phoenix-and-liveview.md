# Phoenix and LiveView

Batch attribution: `liveview-1.0.0`, `liveview-1.1.0`, and `phoenix-1.8.0`.

## Contents

- [Upgrade projects and assets](#upgrade-projects-and-assets)
- [Use generated Phoenix application boundaries](#use-generated-phoenix-application-boundaries)
- [Colocate browser behavior with components](#colocate-browser-behavior-with-components)
- [Render and patch dynamic interfaces](#render-and-patch-dynamic-interfaces)
- [Debug rendered components](#debug-rendered-components)
- [Test rendered behavior](#test-rendered-behavior)

## Upgrade projects and assets

### Install the matching Phoenix generator

Phoenix 1.8 requires Erlang/OTP 25 or later. Install its project generator explicitly when replacing an existing `phx.new` archive:

```console
mix archive.install hex phx_new 1.8.0 --force
```

### Wire the LiveView compiler and test parser

Put LiveView's compiler before the standard compilers, upgrade the dependency, and use LazyHTML in tests:

```elixir
# project/0
compilers: [:phoenix_live_view] ++ Mix.compilers()

# deps/0
{:phoenix_live_view, "~> 1.1"},
{:lazy_html, ">= 0.0.0", only: :test}
```

Remove Floki only if no other dependency or test still uses it. The upgrade can be automated with:

```console
mix archive.install hex igniter_new
mix igniter.upgrade phoenix_live_view
```

If the app enables colocated code, also update esbuild, add `--alias:@=.`, and set `NODE_PATH` to the dependency and build paths.

## Use generated Phoenix application boundaries

### Follow generated project guidance

New `phx.new` applications include an `AGENTS.md` with Phoenix and Elixir syntax, idiom, and API guidance for coding tools working in the repository.

### Treat the default CSS stack as replaceable

New projects include Tailwind v4, daisyUI, light and dark themes, and a layout theme toggle. The `phx.gen.*` generators do not depend on daisyUI, so removing the plugin does not require rewriting generated features.

### Choose authentication behavior explicitly

`mix phx.gen.auth` generates magic-link registration and login by default. Traditional email/password authentication remains opt-in through user settings. Generated authentication includes a `require_sudo_mode` plug for operations that require recent authentication.

### Thread generated scopes through the application

`mix phx.gen.auth` creates an application-owned `%MyApp.Accounts.Scope{}` and uses it as the default scope when none exists. With a default scope, `phx.gen.live`, `phx.gen.html`, and `phx.gen.json`:

- pass `current_scope` through context functions;
- generate scoped queries and foreign keys;
- isolate PubSub topics by scope; and
- place generated LiveView routes in the authenticated `live_session`.

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

### Call layout components explicitly

The root layout remains unchanged, but LiveViews no longer select a fixed app layout with `use Phoenix.LiveView, layout: ...`. Call the layout function component from the rendered page so each layout can accept its own assigns and slots:

```heex
<Layouts.app flash={@flash}>
  <p>My LiveView page</p>
</Layouts.app>
```

## Colocate browser behavior with components

### Define colocated hooks and JavaScript

LiveView extracts a component's `<script>` at compile time. Use `Phoenix.LiveView.ColocatedHook` for hooks and `Phoenix.LiveView.ColocatedJS` for arbitrary JavaScript; the latter may omit `name`.

Colocated hooks require Phoenix 1.8 or newer. A hook name beginning with `.` is prefixed with its module to prevent global collisions. Rename any pre-upgrade global hook that intentionally began with a dot.

```heex
<div id="status" phx-hook=".Status"></div>
<script :type={Phoenix.LiveView.ColocatedHook} name=".Status">
  export default { mounted() { this.el.textContent = "ready" } }
</script>
```

Import and merge the generated hook collection:

```javascript
import {hooks as colocatedHooks} from "phoenix-colocated/my_app"
const liveSocket = new LiveSocket("/live", Socket, {
  hooks: {...colocatedHooks}
})
```

### Use the bundled JavaScript declarations

The JavaScript client ships declarations for every public API, replacing `@types/phoenix_live_view`. Annotate hooks with JSDoc or subclass `ViewHook`:

```javascript
/** @type {import("phoenix_live_view").Hook} */
const Status = { mounted() { this.pushEvent("ready", {}) } }
```

If an editor cannot resolve the declarations, map TypeScript `paths` to both `node_modules/*` and `../deps/*`.

### Support form-associated custom elements

The client treats form-associated custom elements as form inputs, so they participate in LiveView form handling like native controls.

## Render and patch dynamic interfaces

### Key comprehensions with stable identity

Comprehensions perform change tracking by default and use each entry's index when no key is provided. Add `:key` when identity must remain stable across insertions and moves:

```heex
<li :for={item <- @items} :key={item.id}>{item.name}</li>
```

Keys work on ordinary elements and components using `:for`, but not on slot entries or `:for` attached to slots. Prefer streams for very large collections when server memory matters.

### Render through portals

`Phoenix.Component.portal/1` moves rendered content elsewhere in the DOM while retaining event handling in the owning LiveView. It also works from LiveComponents and nested LiveViews:

```heex
<.portal id="tooltip" target="body">
  <div role="tooltip">Saved</div>
</.portal>
```

### Preserve client-controlled attributes

Use `JS.ignore_attributes/1` to keep patches from overwriting attributes controlled by the browser or client code, such as a dialog's `open` state:

```heex
<dialog id="modal" phx-mounted={JS.ignore_attributes(["open"])}>...</dialog>
```

### Update streams without inserting

Pass `update_only: true` when `stream_insert/4` should update an existing item and leave a missing item absent:

```elixir
stream_insert(socket, :items, item, update_only: true)
```

## Debug rendered components

### Annotate component definitions and callers

Enable `debug_heex_annotations` in development to annotate rendered markup with both the function component definition and its caller file and line. `Phoenix.LiveReloader` can use configured key-click navigation to open either source location in the editor:

```elixir
config :phoenix_live_view, debug_heex_annotations: true
```

The annotations also mark slot boundaries. Enable `debug_attributes` to add a tag's source line as `data-phx-loc` and its LiveView PID as `data-phx-pid`:

```elixir
config :phoenix_live_view,
  debug_heex_annotations: true,
  debug_attributes: true
```

Custom `Phoenix.LiveView.TagEngine` implementations must implement `annotate_slot/4`.

### Inspect running LiveViews

Use `Phoenix.LiveView.Debug` to inspect runtime LiveViews. `live_components/1` returns inspection failures as error tuples instead of raising.

### Format custom inline tags

Configure `Phoenix.LiveView.HTMLFormatter` with `:inline_matcher`, a list of strings and regular expressions identifying tag names that should remain inline.

## Test rendered behavior

### Use LazyHTML selectors and text filters

LiveViewTest parses HTML with LazyHTML and supports modern selectors including `:is()` and `:has()`. Text filters normalize whitespace. Floki-only `fl-contains` and `fl-icontains` selectors do not work in `element/3`; replace them with the text-filter argument:

```elixir
view |> element("main a", "Sign up") |> render_click()
```

### Fix duplicate IDs or select an error policy

`LiveViewTest.live/3` and `live_isolated/3` raise by default when the rendered DOM or LiveComponent IDs are duplicated. Fix the IDs or use their `on_error` option to select different behavior.
