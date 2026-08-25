# JavaScript and JSDoc Migration

Batch attribution: `7.0-native-port`.

## Contents

- [Make parameter optionality explicit](#make-parameter-optionality-explicit)
- [Use `typeof` for values in JSDoc type positions](#use-typeof-for-values-in-jsdoc-type-positions)
- [Replace removed Closure-style JSDoc forms](#replace-removed-closure-style-jsdoc-forms)
- [Rewrite constructor-function and prototype patterns as classes](#rewrite-constructor-function-and-prototype-patterns-as-classes)
- [Give variadics real rest syntax](#give-variadics-real-rest-syntax)
- [Describe expression overloads with a callable type](#describe-expression-overloads-with-a-callable-type)
- [Initialize every level of an expando](#initialize-every-level-of-an-expando)
- [Normalize CommonJS patterns](#normalize-commonjs-patterns)
- [Expect JavaScript declaration emit to differ](#expect-javascript-declaration-emit-to-differ)

## Make parameter optionality explicit

The native checker follows TypeScript parameter rules more closely. A JavaScript
parameter annotated as `any`, `unknown`, or `undefined` is no longer implicitly
optional, even when strict mode is disabled.

```js
/** @param {unknown} value */
function consume(value) {}

consume(); // Error: an argument is required.
```

Use optional/default syntax that reflects the actual call contract. Merely
using `arguments` inside a function also no longer synthesizes a rest parameter;
declare a rest parameter when callers may supply additional values.

## Use `typeof` for values in JSDoc type positions

A value name is no longer reinterpreted as `typeof` that value when it appears
where a type is expected. Write the query explicitly:

```js
const FORWARD = 1;
const BACKWARD = 2;

/** @typedef {typeof FORWARD | typeof BACKWARD} Direction */
```

## Replace removed Closure-style JSDoc forms

The native checker drops several legacy spellings:

| Removed form | TypeScript-shaped replacement |
| --- | --- |
| `?` | Use `any` when unknown values are genuinely intended |
| `module:file~name` | Use `import("file").name` |
| `function(string): void` | Use an arrow-function type such as `(value: string) => void` |

The `@class`, `@constructor`, and `@enum` tags no longer provide their previous
typing behavior. Prefer actual classes for construction patterns and `@typedef`
for named type relationships.

## Rewrite constructor-function and prototype patterns as classes

Expando-based constructor functions and later prototype assignments are no
longer recognized as the old checker recognized them. Express the structure
directly:

```js
class Parser {
  parse() {
    return 1;
  }
}
```

This also avoids relying on the removed typing effects of `@class` and
`@constructor`.

## Give variadics real rest syntax

A `...T` JSDoc type is only an array-type synonym; it does not make an ordinary
parameter rest-like. Put `...` in the JavaScript signature:

```js
/** @param {number[]} values */
function sum(...values) {
  return values.reduce((total, value) => total + value, 0);
}
```

## Describe expression overloads with a callable type

`@overload` is ignored on arrow functions and function expressions. Attach a
callable `@type` with each signature instead:

```js
/**
 * @type {{ (x: string): string; (x: number): number }}
 * @param {string | number} x
 * @returns {any}
 */
const identity = x => x;
```

Function declarations may continue using the forms the checker supports; this
restriction is specifically about arrow functions and function expressions.

## Initialize every level of an expando

Nested expando properties require assignments for every intermediate object.
Do not rely on the checker to infer an object that is never created at runtime:

```js
const settings = {};
settings.output = {};
settings.output.format = "esm";
```

## Normalize CommonJS patterns

The native checker no longer gives special module meaning to:

- top-level `this`;
- aliases of `module.exports`; or
- property access directly on a `require()` call, such as
  `require("pkg").property`.

Destructure property imports explicitly. A CommonJS file must also choose
between assigning the whole export and assigning named export properties; do
not mix `module.exports = value` with `module.exports.name = value`.

```js
const { readFile } = require("fs");

module.exports = { readFile };
```

## Expect JavaScript declaration emit to differ

Declaration output from `.js` input is not intended to reproduce the previous
JavaScript compiler's exact `.d.ts` shape. Differences are especially likely
when the source contains suppressed or unsuppressed errors. Tools and tests that
compare declarations structurally or textually must tolerate or deliberately
normalize the native emitter's output.
