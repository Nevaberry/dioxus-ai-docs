# Template Compiler

## Register the TypeScript pre-transform

`@lit-labs/compiler` exports `compileLitTemplates()`, a TypeScript transformer
that optimizes away Lit's prepare render phase. Register it in the `before`
transform list:

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

The transform can also handle JavaScript when those files are passed through
the TypeScript transform. If a JavaScript template remains untouched, verify
the build pipeline includes that file before investigating its template
syntax.

## Preserve template eligibility

Only well-formed templates are optimized. The compiler must also be able to
trace the `html` tag directly to `lit` or `lit-html`.

Eligible import forms include a renamed named import:

```js
import {html as litHtml} from 'lit';

litHtml`<p>${message}</p>`;
```

A namespace import is also eligible:

```js
import * as litModule from 'lit-html';

litModule.html`<p>${message}</p>`;
```

A re-exported `html` tag is not eligible, even if its original source was
`lit` or `lit-html`. Import the tag directly in files whose templates should
be compiled.

Templates with dynamic bindings inside any of these elements are ineligible:

- `textarea`
- `title`
- `style`
- `script`

Move the dynamic value or change the implementation only when doing so
preserves the intended HTML and security behavior. Falling back to normal Lit
rendering is preferable to altering semantics merely to force compilation.

## Inspect emitted output

After a successful transform, emitted code no longer calls the authored
`html` tag. It contains template metadata and creates a result object with
`_$litType$` and `values`:

```js
const b = (strings) => strings;
const template = {
  h: b`<h1>Hello <?></h1>`,
  parts: [{type: 2, index: 1}],
};
const hi = (name) => ({
  _$litType$: template,
  values: [name],
});
```

Exact formatting and local identifiers may vary. The useful verification
signals are:

- The authored tag call is gone.
- Static template metadata is present.
- Runtime values remain in a `values` array.
- The returned object associates those values with `_$litType$`.

Use emitted-code inspection to distinguish a transform configuration problem
from an application runtime problem.

## Avoid the initial adjacent-part bug

Compiler 1.0.1 fixes a bug in compiled templates where adjacent attribute and
element parts could mix up their values. Projects using compiler 1.0.0 should
upgrade.

When diagnosing suspicious value placement:

1. Check the installed compiler version.
2. Upgrade from 1.0.0 before changing the source template.
3. Rebuild from clean generated output.
4. Exercise templates that place attribute and element parts next to one
   another.
5. Only investigate application value ordering if the issue persists on the
   fixed compiler.

## Troubleshooting checklist

If an expected template is not compiled, verify all of the following:

1. `compileLitTemplates()` is registered as a TypeScript `before` transform.
2. The source file passes through that TypeScript transform.
3. The template is well formed.
4. The tag is imported directly from `lit` or `lit-html`.
5. The tag is a supported renamed named import or namespace import, not a
   re-export.
6. No dynamic binding occurs inside `textarea`, `title`, `style`, or `script`.
7. Emitted code is being inspected rather than cached output from an earlier
   build.

The `compiler` guidance applies these checks to both TypeScript and JavaScript
that enters the TypeScript transformation pipeline.

