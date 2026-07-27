# Story authoring and docs

## React CSF factories

React CSF factories have reached Preview status. A typed preview can construct
component metadata and stories without separate `Meta` and `StoryObj` type
declarations:

```ts
import preview from '../.storybook/preview';
import Button from './Button';

const meta = preview.meta({ component: Button });
export const Primary = meta.story({
  args: { label: 'Button', primary: true },
});
```

Older CSF formats remain supported. A codebase can therefore adopt factories
incrementally instead of converting every story in one change.

Factory stories can also use the experimental `.test()` API for named,
story-bound tests; see [Testing and automation](testing-and-automation.md).

## CSF modules and tags

Addon Docs can resolve CSF4 modules that do not have a default export. Do not
add a synthetic default export solely to make such a module visible to Docs.

CSF Next adds tag type support. The `skip` tag propagates to generated `.test`
children, which makes a skip on source story metadata relevant to generated
test execution as well.

## Default tag exclusion

Tag filters can exclude stories that match a tag. `main.ts` can establish the
initial selection:

```ts
export default {
  tags: {
    experimental: { defaultFilterSelection: 'exclude' },
  },
};
```

This controls the initial filter rather than removing the stories from the
project. Use it when content should remain addressable but hidden from the
default navigation view.

## Standalone MDX identity

Standalone MDX supports an explicit `id` on `Meta`:

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

Use an explicit ID when the document needs a stable identity independent of its
derived title or location.

## Docs API changes

- `ExternalDocs` is deprecated. Avoid adding new dependencies on it and include
  it in Docs migration review.
- `ActionItem` accepts `ariaLabel`, allowing an accessible label to be supplied
  when its visual presentation is not sufficient.

## Experimental React docgen service

Enable `features.experimentalDocgenServer` to use a worker-backed service that
unifies React component metadata across MCP, Docs, and Controls:

```js
export default {
  features: { experimentalDocgenServer: true },
};
```

When enabled, ArgTypes and Controls consume this service as well, including
metadata from `react-component-meta`. Diagnose inconsistencies at the shared
metadata service rather than assuming each consumer has an independent docgen
pipeline.

Batch attribution: `9.0-10.0`, `10.5.0`.
