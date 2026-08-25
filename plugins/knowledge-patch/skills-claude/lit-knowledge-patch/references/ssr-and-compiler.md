# SSR and Compiler

This reference groups server-rendering compatibility (`ssr-3.3-4.x`) and
template compilation (`compiler`) by the build and runtime tasks they affect.

## SSR Lifecycle Callbacks

Lit SSR 3.3 adds event handling and can call `connectedCallback()` during SSR.
Enable the callback behavior globally before rendering:

```js
globalThis.litSsrCallConnectedCallback = true;
```

Starting in SSR 4.1, `LitElementRenderer` also has configuration for:

- disabling SSR;
- calling `connectedCallback()` on `LitElement` subclasses.

Configure the renderer intentionally when a component's connection callback
sets up state required by its server-rendered output.

## Custom Renderer Migration for SSR 4.0

SSR 4.0 replaces generator use throughout the `ElementRenderer` interface with
a thunk/trampoline pattern. This is a breaking interface change.

Before moving a custom renderer from 3.x to 4.0:

1. Inventory its `ElementRenderer` methods and generator delegation.
2. Replace generator-based returns and control flow with the new
   thunk/trampoline form.
3. Test component rendering through the custom renderer.

Do not treat a 3.x custom renderer as source-compatible with 4.0.

## SSR DOM Shim in 4.1

The SSR DOM shim implements:

- `ShadowRoot`;
- `MutationObserver`;
- `ResizeObserver`;
- `IntersectionObserver`.

It also includes `document` in event paths. Components that reference these
browser APIs while rendering can run against the shim, including event-path
logic that expects the document.

## Node Typings in SSR 4.0

`@types/node` is a ranged peer dependency rather than a package dependency.
This prevents the SSR package from forcing a conflicting Node typings version
into a consumer project.

Consumers that need Node typings must satisfy that peer dependency with an
appropriate version in their own dependency setup.

## Register the Template Compiler

`@lit-labs/compiler` exports `compileLitTemplates()`, a TypeScript transformer
that optimizes away Lit's prepare render phase. Register it as a pre-transform:

```js
import typescript from '@rollup/plugin-typescript';
import {compileLitTemplates} from '@lit-labs/compiler';

export default {
  plugins: [
    typescript({
      transformers: {
        before: [compileLitTemplates()],
      },
    }),
  ],
};
```

The transformer also handles JavaScript files when they are passed through the
TypeScript transform.

## Keep Templates Eligible

Only well-formed templates whose `html` tag is imported directly from `lit` or
`lit-html` are optimized.

Eligible import forms include a renamed named import and a namespace import:

```js
import {html as litHtml} from 'lit';
import * as litModule from 'lit-html';

litHtml`<p>${message}</p>`;
litModule.html`<p>${message}</p>`;
```

A re-exported tag is not eligible. A template is also ineligible when it has a
dynamic binding inside any of these elements:

- `textarea`
- `title`
- `style`
- `script`

When a template is not transformed, check tag provenance, template
well-formedness, and binding location before debugging the build integration.

## Verify Emitted Output

A successfully transformed template no longer calls the authored `html` tag.
The emitted code contains template metadata and returns an object with
`_$litType$` and `values`:

```js
const b = (strings) => strings;
const template = {
  h: b`<h1>Hello <?></h1>`,
  parts: [{type: 2, index: 1}],
};
const hi = (name) => ({_$litType$: template, values: [name]});
```

Use those structural markers to distinguish transformed output from an
uncompiled template.

## Avoid the Compiler 1.0.0 Adjacent-Part Bug

Compiler 1.0.0 can mix up values in a compiled template when an attribute part
and an element part are adjacent. Compiler 1.0.1 fixes the defect.

Upgrade projects using 1.0.0, then test a template containing adjacent
attribute and element parts to confirm the corrected value placement.
