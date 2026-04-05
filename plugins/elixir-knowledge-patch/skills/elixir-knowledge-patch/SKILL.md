---
name: elixir-knowledge-patch
description: "Elixir 1.19–1.20, Phoenix 1.8, LiveView 1.0–1.1: type system inference, map key typing, colocated hooks, portals, scopes, magic link auth, new APIs and breaking changes."
version: "1.20.0-rc"
license: MIT
metadata:
  author: Nevaberry
  tags:
    - elixir
    - phoenix
    - liveview
    - type-system
    - otp
---

# Elixir Knowledge Patch (1.19–1.20, Phoenix 1.8, LiveView 1.0–1.1)

**Baseline**: Elixir 1.16, OTP 26, Phoenix 1.7, LiveView 0.x (pre-1.0), Ecto 3.11, GenServer, Supervisor, mix, ExUnit, dbg macro.

This patch covers Elixir 1.19–1.20-rc, Phoenix 1.8, and LiveView 1.0–1.1 (2024-12 to 2026-01).

## Index

| Topic | File | Key Features |
|-------|------|--------------|
| Type System & Inference | [references/elixir-type-system.md](references/elixir-type-system.md) | Full expression inference, map key typing, struct update deprecation |
| APIs, Mix & Compilation | [references/elixir-apis-and-mix.md](references/elixir-apis-and-mix.md) | New stdlib APIs, mix commands, lazy module loading, deprecations |
| LiveView JS & Hooks | [references/liveview-js-and-hooks.md](references/liveview-js-and-hooks.md) | JS command targeting, colocated hooks, ViewHook class, programmable JS |
| LiveView Templates & Streams | [references/liveview-templates-and-streams.md](references/liveview-templates-and-streams.md) | Keyed comprehensions, portals, `ignore_attributes`, LazyHTML migration |
| Phoenix 1.8 | [references/phoenix-1-8.md](references/phoenix-1-8.md) | Scopes, magic link auth, simplified layouts, security headers |

---

## Quick Reference

### Elixir 1.20 Type Inference

The compiler infers types from all expressions (not just patterns). Backward inference narrows argument types:

```elixir
def sum_to_string(a, b), do: Integer.to_string(a + b)
# Infers a, b must be integer() (not float) because Integer.to_string requires integer
```

Cross-clause inference — later clauses know what previous clauses matched:

```elixir
case System.get_env("VAR") do
  nil -> :not_found
  value -> String.upcase(value)  # value is binary(), not nil
end
```

### Map Key Typing (1.20)

```elixir
Map.put(map, :key, 123)      #=> %{..., key: integer()}
Map.delete(map, :key)         #=> %{..., key: not_set()}
Map.replace(map, :key, 123)   #=> %{..., key: if_set(integer())}
```

### Struct Update Deprecation (1.19)

```elixir
# Deprecated — requires prior pattern match:
def update(uri), do: %URI{uri | path: "/foo"}

# Correct:
def update(%URI{} = uri), do: %{uri | path: "/foo"}
```

### New APIs at a Glance

| API | Version | Purpose |
|-----|---------|---------|
| `Access.values/0` | 1.19 | Traverse all values in maps/keyword lists |
| `String.count/2` | 1.19 | Count pattern occurrences in string |
| `min/2`, `max/2` in guards | 1.19 | Guard-compatible min/max |
| `Integer.ceil_div/2` | 1.20 | Ceiling division |
| `Integer.popcount/1` | 1.20 | Count set bits |
| `IO.iodata_empty?/1` | 1.20 | Check if iodata is empty |
| `List.first!/1`, `List.last!/1` | 1.20 | Raise on empty list |

### Breaking Changes (1.20)

```elixir
# map.foo() with parens now RAISES (not warns) — use map.foo
# mod.foo without parens now RAISES — use mod.foo()

# File.stream! arg order swapped:
File.stream!(path, lines_or_bytes, modes)  # NEW order

# Bitstring size requires pin:
<<data::size(^size)>>  # was <<data::size(size)>>
```

### LiveView Colocated Hooks (1.1)

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

### LiveView Portals (1.1)

```heex
<.portal id="my-tooltip" target="body">
  <div class="tooltip">Content here</div>
</.portal>
```

### Phoenix 1.8 Scopes

```elixir
# Generated context functions take scope as first arg
def list_posts(%Scope{} = scope) do
  Repo.all(from p in Post, where: p.user_id == ^scope.user.id)
end

# LiveViews use socket.assigns.current_scope
def mount(_params, _session, socket) do
  Blog.subscribe_posts(socket.assigns.current_scope)
  {:ok, stream(socket, :posts, Blog.list_posts(socket.assigns.current_scope))}
end
```

### Phoenix 1.8 Simplified Layouts

```heex
<Layouts.app flash={@flash}>
  <:breadcrumb><.link navigate={~p"/posts"}>Posts</.link></:breadcrumb>
  <p>My content</p>
</Layouts.app>
```

Single `root.html.heex` layout. Multiple app layouts: `<Layouts.admin>`, `<Layouts.cart>`, etc.

### JS Command Targeting (LiveView 1.0)

```elixir
<button phx-click={JS.add_class("highlight", to: {:closest, "tr"})}>Select</button>
<div phx-click={JS.show(to: {:inner, ".details"})}>Expand</div>
```

### Keyed Comprehensions (LiveView 1.1)

```heex
<li :for={item <- @items} :key={item.id}>{item.name}</li>
```
