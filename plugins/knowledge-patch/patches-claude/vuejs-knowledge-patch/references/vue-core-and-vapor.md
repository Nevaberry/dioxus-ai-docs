# Vue Core and Release Channels

## Explicitly type template refs

Vue exports `TemplateRef` for explicitly typing values returned by
`useTemplateRef` (since 3.5.14).

```ts
import { useTemplateRef, type TemplateRef } from 'vue'

const input: TemplateRef<HTMLInputElement> =
  useTemplateRef<HTMLInputElement>('input')
```

## Track stable and prerelease channels separately

The release-channel catalog snapshot recorded `v3.5.39` as Vue core's stable
tag and `v3.6.0-beta.17` as its 3.6 prerelease. Stable release details live in
`CHANGELOG.md` on the `main` branch; prerelease details live on the `minor`
branch. Do not treat a prerelease tag as the stable line. Later 3.5 patch
guidance below supersedes that snapshot where applicable.

## Hydration and SSR correctness

### Preserve namespaces for dynamic props

Vue passes an element's namespace while patching dynamic properties during
hydration (since 3.5.40). SVG and other namespaced elements therefore receive
the appropriate property behavior; hydration tests should retain their actual
namespace.

### Preserve pre-hydration text input

Hydration preserves text entered through `v-model` before hydration begins
(since 3.5.41). Avoid application-level workarounds that overwrite the user's
early input.

### Escape SSR comments safely

SSR comment escaping no longer produces closing comment delimiters (since
3.5.40), preventing escaped input from ending its surrounding comment.

## Forms, slots, and transitions

### Respect changing select model types

`<select v-model>` updates use the model's current value type (since 3.5.40),
including when that type changes during the binding's lifetime.

### Pass nullish slot-prop objects directly

Object-form `v-bind` on a slot outlet accepts `null` and `undefined` (since
3.5.41). Optional slot-prop objects no longer need an empty-object fallback.

```vue
<slot v-bind="maybeProps" />
```

### Transition teleported content

A `<Teleport>` may be the child of `<Transition>` (since 3.5.41), allowing
teleported content to participate in transitions.

```vue
<Transition name="fade">
  <Teleport v-if="open" to="body">
    <div>Dialog</div>
  </Teleport>
</Transition>
```

## Component and custom-element types

Component public-instance `$el` is no longer constrained to `Element` (since
3.5.40), so renderers can represent other host-node types.

Vue warns when a custom-element prop overrides a native property (since
3.5.41). Treat the warning as an ambiguous property design rather than
assuming the custom prop silently wins.

`defineModel()` retains model type inference when its default is a factory
(since 3.5.41). Explicit type annotations used only to compensate for the old
inference loss can be reconsidered.
