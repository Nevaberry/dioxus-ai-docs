# LiveView JS & Hooks

## JS Command Targeting with Tuples (LiveView 1.0)

JS commands support `{:inner, selector}` and `{:closest, selector}` for relative targeting:

```elixir
# Target closest table row from clicked element
<button phx-click={JS.add_class("highlight", to: {:closest, "tr"})}>Select</button>

# Target first link inside a container
<div phx-click={JS.show(to: {:inner, ".details"})}>Expand</div>
```

## Programmable JS Commands from Hooks (LiveView 1.0)

Hooks can call JS commands (`show`, `hide`, `addClass`, etc.) programmatically, integrating with server DOM patching:

```javascript
this.js("show", {to: "#modal"})
this.js("addClass", {names: ["active"], to: "#tab-1"})
```

## `createHook` for Custom Elements (LiveView 1.0)

Export `createHook` from `phoenix_live_view` enables using hooks with Web Components/Custom Elements.

## `blocking: false` on JS Transitions (LiveView 1.0)

Prevents JS transitions from blocking DOM updates:

```elixir
JS.show(transition: {"fade-in", "", "opacity-100"}, blocking: false)
```

## Hook `pushEvent` Returns a Promise (LiveView 1.0)

```javascript
let {reply} = await this.pushEvent("validate", {data: value})
```

## Colocated Hooks (LiveView 1.1)

Write hook JS inline in HEEx templates. Hook names starting with `.` are auto-prefixed with the module name:

```elixir
<div id="sortable" phx-hook=".Sortable">...</div>
<script :type={Phoenix.LiveView.ColocatedHook} name=".Sortable">
  export default {
    mounted() { /* JS code here */ }
  }
</script>
```

Setup: add `:phoenix_live_view` to `compilers:` in `mix.exs`, import in `app.js`:

```javascript
import {hooks as colocatedHooks} from "phoenix-colocated/my_app"
const liveSocket = new LiveSocket("/live", Socket, {hooks: {...colocatedHooks}})
```

For non-hook JS, use `ColocatedJS` script type (no `name` needed). Requires Phoenix 1.8+:

```elixir
<script :type={Phoenix.LiveView.ColocatedJS}>
  // standalone JS code here
</script>
```

## ViewHook Class & JS Types (LiveView 1.1)

Hooks can now be defined as classes. Official TypeScript types ship with the package:

```javascript
import {LiveSocket, ViewHook} from "phoenix_live_view"
class MyHook extends ViewHook {
  mounted() { /* ... */ }
}
```

## LiveView 1.0 Deprecations & Removals

- `phx-feedback-for` removed → use `Phoenix.Component.used_input?/1`
- `phx-page-loading` removed → use `page_loading: true` on `JS.push/2`
- `dynamic_tag/1`: `name` attr deprecated → use `tag_name`
- `push_redirect` deprecated → `push_navigate`
- `live_flash` deprecated → `Phoenix.Flash.get`
