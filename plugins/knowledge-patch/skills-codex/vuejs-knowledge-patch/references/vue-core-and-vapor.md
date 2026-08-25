# Vue Core and Release Channels

## TypeScript APIs

### Type template refs explicitly (since 3.5.14)

Vue exports `TemplateRef` for explicit typing of refs returned by
`useTemplateRef()`.

```ts
import { useTemplateRef, type TemplateRef } from 'vue'

const input: TemplateRef<HTMLInputElement> =
  useTemplateRef<HTMLInputElement>('input')
```

### Allow host-specific component elements (since 3.5.40)

Component public-instance typing no longer constrains `$el` to `Element`. This
allows renderers with non-`Element` host-node types to represent `$el`
accurately.

### Preserve `defineModel()` factory inference (Vue 3.5.41)

This item is carried by batch 3.5.40. The 3.5.41 fixes retain the inferred model type when a
`defineModel()` default is supplied as a factory. Remove workarounds that widen
or manually restate the model type only after verifying the project uses the
fixed runtime and declarations.

## Hydration and SSR

### Patch dynamic props with the element namespace (since 3.5.40)

Hydration passes the element namespace while patching dynamic props. This gives
SVG and other namespaced elements the correct property behavior during
hydration.

### Preserve pre-hydration text input (Vue 3.5.41)

This item is carried by batch 3.5.40. The 3.5.41 hydration behavior preserves text entered through
`v-model` before hydration starts instead of overwriting the user's input.
Include typed-ahead input in hydration regression tests.

### Escape SSR comments safely (since 3.5.40)

SSR comment escaping no longer produces closing comment delimiters. Escaped
content therefore cannot accidentally terminate its surrounding comment.

## Templates and built-in components

### Respect the current select-model type (since 3.5.40)

`<select v-model>` updates use the model's current type, including when that
type changes during the lifetime of the binding. Test both the initial and
changed types when options depend on typed values.

### Bind nullish slot-prop objects directly (Vue 3.5.41)

This item is carried by batch 3.5.40. The 3.5.41 behavior accepts `null` and `undefined` in object-form
`v-bind` on slot outlets. Optional slot-prop objects no longer need an
empty-object fallback.

```vue
<slot v-bind="maybeProps" />
```

### Transition teleported content (Vue 3.5.41)

This item is carried by batch 3.5.40. The 3.5.41 behavior supports `<Teleport>` as a `<Transition>` child,
allowing teleported content to participate in transitions.

```vue
<Transition name="fade">
  <Teleport v-if="open" to="body">
    <div>Dialog</div>
  </Teleport>
</Transition>
```

## Custom elements

This item is carried by batch 3.5.40. Vue 3.5.41 warns in development when a custom-element prop
overrides a native property. Treat the warning as an ambiguity to resolve; do
not silently rely on the collision.

## Release channels

The `vue-core-release-catalog` snapshot from 2026-07-15 records the stable tag
as `v3.5.39` and the 3.6 prerelease as `v3.6.0-beta.17`; later stable items in
this stream supersede that snapshot's "latest stable" status. Stable release
details are kept in `CHANGELOG.md` on the `main` branch, while prerelease
details are maintained on the `minor` branch. Consult the branch matching the
release channel instead of assuming both histories live in the same changelog.
