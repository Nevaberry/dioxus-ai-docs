# Rules, Tests, and Integrations

Use this reference for custom rule migration, stricter tests, scope and AST
behavior, typed packages, formatter context, and rule-level fixes.

## Removed `context` APIs

Since 10.0.0, custom rules and plugins must replace removed accessors with
properties.

| Removed API | Replacement |
| --- | --- |
| `context.getCwd()` | `context.cwd` |
| `context.getFilename()` | `context.filename` |
| `context.getPhysicalFilename()` | `context.physicalFilename` |
| `context.getSourceCode()` | `context.sourceCode` |
| `context.parserOptions` | `context.languageOptions` or `context.languageOptions.parserOptions` |

`context.parserPath` has no replacement. Redesign integrations that depended
on the parser's module path rather than emulating the deleted property.

## Removed `SourceCode` APIs

Since 10.0.0, use the supported token and spacing methods.

| Removed API | Replacement |
| --- | --- |
| `getTokenOrCommentBefore()` | `getTokenBefore()` with `{ includeComments: true }` |
| `getTokenOrCommentAfter()` | `getTokenAfter()` with `{ includeComments: true }` |
| `isSpaceBetweenTokens()` | `isSpaceBetween()` |

`SourceCode#getJSDocComment()` has no replacement. Treat JSDoc discovery as a
redesign point instead of preserving the old call shape.

## Strict `RuleTester` assertions

Since 10.0.0, `RuleTester#run()` accepts an `assertionOptions` object that can
require complete expected errors.

- `requireMessage: true` permits either `message` or `messageId`.
- `requireMessage: "message"` requires the literal `message` form.
- `requireMessage: "messageId"` requires the `messageId` form.
- `requireLocation: true` requires both `line` and `column`.
- `requireData: true` requires `data` when the chosen `messageId` template has
  placeholders.

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

Select only the guarantees that are part of the rule's public contract. Before
enabling `requireData`, inspect the selected message template to see whether it
contains placeholders.

## JSX identifiers participate in scope analysis

Since 10.0.0, an identifier such as `Card` in `<Card />` is a normal reference
to the in-scope variable. Scope-sensitive rules should not:

- report an imported component as unused solely because its only use is JSX;
- miss an undefined component solely because its use is JSX.

Update expected diagnostics in scope analyzers and rule tests accordingly.

## `max-params` and TypeScript `this`

Since 10.0.0, `max-params` supports `countThis: "never"`. It excludes a
TypeScript `this` parameter from the count and supersedes the deprecated
`countVoidThis` option.

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

## ES2026 `Temporal`

Since 10.2.0, ES2026 globals include `Temporal`, and `no-obj-calls` recognizes
it as a non-callable object. With ES2026 globals enabled, `Temporal()` is
reported as an invalid object call rather than as an undefined identifier.

## Safer `no-var` fixes in TypeScript modules

Since 10.2.0, `no-var` can apply its fix inside TypeScript `TSModuleBlock`
nodes. It withholds the autofix if the variable is used before its declaration,
preventing a potentially unsafe conversion.

## Safer removal edits

Since 10.8.1, the `no-unused-labels` autofix and the `removeVar` suggestion
from `no-unused-vars` account for automatic semicolon insertion. Removing code
no longer risks joining adjacent syntax in a way that changes the parse.

## Meta-property names and identifier rules

Since 10.8.1, `id-denylist` and `id-match` ignore names inside meta-properties.
Grammar-defined names such as `meta` in `import.meta` and `target` in
`new.target` no longer produce naming-policy diagnostics.

## Accessor rule corrections

Since 10.8.1, `getter-return` and `accessor-pairs` avoid the false-positive
diagnostics corrected in that release. Re-enable or re-check these rules if a
project disabled them or added suppressions to work around those findings.

## `Program.range` spans the whole source

Since 10.0.0, the `Program` AST node's range includes leading and trailing
comments and whitespace. Integrations must not use `Program.range` as a proxy
for only the narrower inner program content.

## Bundled type definitions

Since 10.0.0, Espree 11.1.0 and ESLint Scope 9.1.0 ship built-in type
definitions. These replace declarations formerly supplied by `@types/espree`
and `@types/eslint-scope`.

The bundled declarations are not identical to the external declaration
packages. Remove duplicate types, then compile typed integrations and adjust
any assumptions exposed by the new definitions.

ESLint 10.2.0 also documents TypeScript 5.3 as the minimum supported version.
Check this floor when compiling parser, scope-manager, or other typed
integrations.

## Formatter color intent

Since 10.0.0, the CLI passes explicit color intent in the second argument to a
formatter's `format()` method:

- `--color` supplies `color: true`.
- `--no-color` supplies `color: false`.

Custom formatters can honor this value instead of inferring the user's choice
from terminal capabilities.
