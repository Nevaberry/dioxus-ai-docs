# Story Authoring and Docs

## React CSF factories

React CSF factories reached Preview status in batch `9.0-10.0`. A typed preview
can create component metadata and stories without separate `Meta` and
`StoryObj` type declarations:

```ts
import preview from '../.storybook/preview';
import Button from './Button';

const meta = preview.meta({ component: Button });
export const Primary = meta.story({
  args: { label: 'Button', primary: true },
});
```

Older CSF formats remain supported. Migrate story files incrementally rather
than coupling factory adoption to a repository-wide rewrite.

Factory stories can also attach experimental named tests through `.test()`;
see [Testing and automation](testing-and-automation.md) for the testing
context and test-only story behavior.

## Tags and filtering

### Set the default filter state

Tag filters can exclude matching stories, and `main.ts` can establish the
initial filter state (batch `9.0-10.0`):

```ts
export default {
  tags: {
    experimental: { defaultFilterSelection: 'exclude' },
  },
};
```

Use this for initial presentation, not as a substitute for removing stories
that must never be indexed.

### Type and propagate tags

CSF Next supports tag types (since `10.5.0`). A `skip` tag propagates to
generated `.test` children, so tag inheritance can suppress both a story and
its derived tests.

When a generated test is unexpectedly absent, inspect the parent story's tags
before changing test registration.

## CSF modules and addon Docs

Addon Docs can resolve CSF4 modules with no default export (since `10.5.0`). Do
not add a synthetic default export only to make such a module visible to Docs.

This is specifically a CSF4 module-resolution behavior; keep existing default
exports where older formats or other tooling still rely on them.

## MDX and Docs APIs

### Give standalone MDX an explicit identity

Standalone MDX accepts an explicit `id` on `Meta` (since `10.5.0`):

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

Use a stable ID when other Docs content or automation addresses the page by
identity rather than title.

### Update Docs components

`ActionItem` accepts `ariaLabel` (since `10.5.0`). Supply it when the visible
content does not provide an adequate accessible name.

`ExternalDocs` is deprecated in `10.5.0`. Avoid introducing new uses and
include replacement work in Docs migrations that currently depend on it.

## Unified React component metadata

Enable the experimental worker-backed React docgen service with
`features.experimentalDocgenServer` (since `10.5.0`):

```js
export default {
  features: { experimentalDocgenServer: true },
};
```

When enabled, one service supplies React component metadata across MCP, Docs,
and Controls. ArgTypes and Controls consume the service, including
`react-component-meta` data.

Use the flag when inconsistent metadata across those surfaces is more costly
than adopting an experimental service. Verify generated ArgTypes and Controls
for representative components before enabling it broadly.
