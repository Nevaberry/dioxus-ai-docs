# Vue Core and Release Channels

## Explicit template-ref types

Vue exports `TemplateRef` for explicitly typing refs created by
`useTemplateRef` (3.5.14):

```ts
import { useTemplateRef, type TemplateRef } from 'vue'

const input: TemplateRef<HTMLInputElement> =
  useTemplateRef<HTMLInputElement>('input')
```

## Stable and prerelease changelogs

At the release-catalog snapshot, the latest stable Vue core tag is `v3.5.39`
and the prerelease line is at `v3.6.0-beta.17`. Stable release details are kept
in `CHANGELOG.md` on the `main` branch; prerelease details are kept in the
changelog on the `minor` branch. Check the appropriate branch when investigating
a behavior that differs between the stable and prerelease channels.
