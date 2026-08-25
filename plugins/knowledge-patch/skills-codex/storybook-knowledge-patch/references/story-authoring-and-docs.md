# Story authoring and docs

## CSF authoring

### React CSF factories

React CSF factories reached Preview status in batch `9.0-10.0`. A typed preview
creates component metadata and stories without separate `Meta` and `StoryObj`
type declarations:

```ts
import preview from '../.storybook/preview';
import Button from './Button';

const meta = preview.meta({ component: Button });
export const Primary = meta.story({
  args: { label: 'Button', primary: true },
});
```

Older CSF formats remain supported. Migrate incrementally instead of rewriting
all story modules solely to adopt factories.

### CSF modules without default exports

Addon Docs resolves CSF4 modules that have no default export (since `10.5.0`).
Do not add a synthetic default export only to make such a module visible to
Docs.

## Tags and filtering

### Initial tag exclusion

Tag filters can exclude matching stories, and `main.ts` can establish the
initial filter state (batch `9.0-10.0`):

```ts
export default {
  tags: {
    experimental: { defaultFilterSelection: 'exclude' },
  },
};
```

This chooses the initial view; users can still change the active filter.

### Typed and inherited tags

CSF Next adds tag type support (since `10.5.0`). A `skip` tag propagates to
generated `.test` children. When a generated test does not run, inspect tags on
the parent story before treating it as a discovery failure.

## MDX and Docs APIs

### Standalone MDX identity

Standalone MDX accepts an explicit `id` on `Meta` (since `10.5.0`):

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

Use an explicit ID when stable cross-links or an identity independent of the
display title is required.

### Docs component changes

`ExternalDocs` is deprecated (since `10.5.0`); avoid introducing new uses and
plan to replace existing ones. `ActionItem` accepts `ariaLabel`, enabling an
accessible label when visible content does not provide one.

## React metadata and docgen

### Worker-backed metadata service

Enable `features.experimentalDocgenServer` for a worker-backed React docgen
service (since `10.5.0`):

```js
export default {
  features: { experimentalDocgenServer: true },
};
```

When enabled, the service unifies React component metadata across MCP, Docs,
and Controls. ArgTypes and Controls consume it, including data from
`react-component-meta`.

Because this service is experimental, keep generated Args and Controls under
test when adopting it in a documentation-heavy project.
