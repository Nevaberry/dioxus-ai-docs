# Rules, Tests, and Integrations

Use this reference when updating custom rules, strengthening rule tests,
maintaining formatters, or reconciling scope, AST, and typed integrations.

## Removed rule APIs

Deprecated rule APIs are removed (since 10.0.0). Replace `context` calls with
the corresponding properties:

| Removed | Replacement |
| --- | --- |
| `context.getCwd()` | `context.cwd` |
| `context.getFilename()` | `context.filename` |
| `context.getPhysicalFilename()` | `context.physicalFilename` |
| `context.getSourceCode()` | `context.sourceCode` |
| `context.parserOptions` | `context.languageOptions` or `context.languageOptions.parserOptions` |

`context.parserPath` has no replacement. Redesign code that depends on it.

The removed `SourceCode` methods have these replacements:

| Removed | Replacement |
| --- | --- |
| `getTokenOrCommentBefore()` | `getTokenBefore()` with `{ includeComments: true }` |
| `getTokenOrCommentAfter()` | `getTokenAfter()` with `{ includeComments: true }` |
| `isSpaceBetweenTokens()` | `isSpaceBetween()` |

`SourceCode#getJSDocComment()` has no replacement. Redesign that dependency
instead of trying to preserve the removed call.

## `RuleTester` assertion requirements

`RuleTester#run()` accepts `assertionOptions` (since 10.0.0):

- `requireMessage: true` accepts either `message` or `messageId`.
- `requireMessage: "message"` requires the literal `message` form.
- `requireMessage: "messageId"` requires the `messageId` form.
- `requireLocation: true` requires both `line` and `column`.
- `requireData: true` requires `data` when the selected `messageId` template
  contains placeholders.

```js
ruleTester.run("my-rule", rule, {
  valid: [],
  invalid: [{
    code: "foo",
    errors: [{
      messageId: "unexpected",
      data: { name: "foo" },
      line: 1,
      column: 1
    }]
  }],
  assertionOptions: {
    requireMessage: "messageId",
    requireLocation: true,
    requireData: true
  }
});
```

Choose the strictness that reflects the rule's public contract. When enabling
`requireData`, inspect the message template before deciding whether the case
needs a `data` object.

## TypeScript `this` parameters in `max-params`

The `max-params` rule accepts `countThis: "never"` (since 10.0.0). It excludes
a TypeScript `this` parameter from the parameter count and supersedes the
deprecated `countVoidThis` option.

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

## JSX identifiers participate in scope analysis

An identifier such as `Card` in `<Card />` is a normal reference to the
in-scope variable (since 10.0.0). Update scope-based rules and their expected
diagnostics accordingly:

- do not report an imported JSX component as unused solely because its use is
  in JSX;
- do not miss an undefined component solely because its use is in JSX.

## Whole-source `Program.range`

The `Program` AST node's `range` includes the whole source, including leading
and trailing comments and whitespace (since 10.0.0). Integrations that assumed
the earlier narrower span must not treat `Program.range` as the range of only
the inner program content.

## Built-in types for Espree and ESLint Scope

Espree 11.1.0 and ESLint Scope 9.1.0 include built-in type definitions (since
10.0.0), replacing declarations previously supplied by `@types/espree` and
`@types/eslint-scope`.

The built-in declarations are not identical to those packages. Remove the
superseded declaration dependency, then expect typed integrations to require
adjustments rather than assuming a drop-in replacement.

## Formatter color intent

The second argument to a formatter's `format()` method carries explicit CLI
color intent (since 10.0.0):

- `--color` passes `color: true`.
- `--no-color` passes `color: false`.

Custom formatters can inspect that value and honor the user's explicit style
choice.

## `Temporal` and `no-obj-calls`

The ES2026 globals include `Temporal` (since 10.2.0). `no-obj-calls`
recognizes it as a non-callable object, so with ES2026 globals enabled,
`Temporal()` is reported instead of being treated as an undefined name.

## Safer `no-var` fixes in TypeScript modules

`no-var` can apply its fix inside TypeScript `TSModuleBlock` nodes (since
10.2.0). It withholds an autofix when a variable is used before its
declaration, avoiding a potentially unsafe conversion.

## Removal edits and automatic semicolon insertion

The `no-unused-labels` autofix and the `removeVar` suggestion from
`no-unused-vars` account for automatic semicolon insertion when removing code
(fixed in 10.8.1). Applying either edit no longer risks joining adjacent
syntax in a way that changes how the result parses.

## Meta-property names and identifier policies

`id-denylist` and `id-match` ignore names in meta-properties (fixed in
10.8.1). Grammar-defined names such as `meta` in `import.meta` and `target` in
`new.target` no longer produce naming-policy diagnostics.

## Accessor-rule corrections

`getter-return` and `accessor-pairs` no longer produce the false-positive
diagnostics corrected in 10.8.1. Projects that disabled or suppressed either
rule to work around those diagnostics should re-check those exceptions after
upgrading.
