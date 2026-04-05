# LiveView Templates & Streams

## Keyed Comprehensions (LiveView 1.1)

Comprehensions now have automatic change tracking (index-based). Add `:key` for optimal diffs:

```heex
<li :for={item <- @items} :key={item.id}>{item.name}</li>
```

Slots are also change-tracked now. `:key` works on components too, but NOT on `:for` on slots.

## Portals (LiveView 1.1)

Teleport content outside its DOM hierarchy (like React's `createPortal`):

```heex
<.portal id="my-tooltip" target="body">
  <div class="tooltip">Content here</div>
</.portal>
```

Works with LiveComponents and nested LiveViews. Events still handled by correct LiveView.

## JS.ignore_attributes (LiveView 1.1)

Prevent LiveView from patching specific attributes (useful for browser-controlled attrs like `open`):

```heex
<details phx-mounted={JS.ignore_attributes(["open"])}>...</details>
```

## stream_insert :update_only (LiveView 1.1)

`stream_insert/4` now accepts `:update_only` — only updates existing items, skips if not present.

## Breaking: Floki → LazyHTML (LiveView 1.1)

LiveViewTest uses LazyHTML (lexbor-based). Replace `fl-contains`/`fl-icontains` selectors:

```diff
- |> element(~s|main a:fl-contains("Sign up")|)
+ |> element("main a", "Sign up")
```

Add `{:lazy_html, ">= 0.0.0", only: :test}` to deps. LiveViewTest now raises on duplicate DOM IDs by default.
