# Rules, Tests, and Integrations

The changes in this reference apply to ESLint 10.0.0 unless a component
version is stated explicitly.

## Removed rule-context APIs

Custom rules and plugins must replace removed methods and properties:

| Removed API | Replacement |
| --- | --- |
| `context.getCwd()` | `context.cwd` |
| `context.getFilename()` | `context.filename` |
| `context.getPhysicalFilename()` | `context.physicalFilename` |
| `context.getSourceCode()` | `context.sourceCode` |
| `context.parserOptions` | `context.languageOptions` or `context.languageOptions.parserOptions` |
| `context.parserPath` | No replacement |

Do not invent a property substitute for `context.parserPath`; it was removed
without a replacement.

## Removed `SourceCode` APIs

Use the current token and spacing methods:

| Removed API | Replacement |
| --- | --- |
| `SourceCode#getTokenOrCommentBefore()` | `getTokenBefore()` with `{ includeComments: true }` |
| `SourceCode#getTokenOrCommentAfter()` | `getTokenAfter()` with `{ includeComments: true }` |
| `SourceCode#isSpaceBetweenTokens()` | `isSpaceBetween()` |
| `SourceCode#getJSDocComment()` | No replacement |

The `includeComments` option is essential when preserving the semantics of
the two removed token-or-comment helpers. `getJSDocComment()` has no direct
replacement, so callers need a different design for that behavior.

## `RuleTester` assertion requirements

`RuleTester#run()` accepts `assertionOptions` alongside `valid` and
`invalid` cases. It can require error cases to exercise a particular part of
the reporting contract:

- `requireMessage: true` allows either `message` or `messageId`.
- `requireMessage: "message"` requires the exact `message` form.
- `requireMessage: "messageId"` requires the exact `messageId` form.
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

`requireData` is conditional on placeholders: a `messageId` alone does not
make `data` mandatory when its template has none.

## TypeScript `this` and `max-params`

The new `countThis: "never"` option makes `max-params` exclude a TypeScript
`this` parameter from its count. This option supersedes the deprecated
`countVoidThis`.

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

Use `countThis` when migrating configuration that used `countVoidThis` or
when a TypeScript receiver annotation should not consume the parameter
limit.

## JSX identifiers participate in scope

An identifier such as `Card` in `<Card />` is a normal reference to its
in-scope variable. Scope-aware rules consequently no longer consider an
imported JSX component unused merely because its only use is in JSX, and no
longer overlook an undefined component merely because the reference is JSX.

Update custom scope-based rule expectations and fixtures that encoded the
older treatment of JSX identifiers.

## Whole-source `Program.range`

The `Program` AST node range spans the whole source. Leading and trailing
comments and whitespace are included, rather than leaving the range at its
previous narrower content boundaries.

Any integration that slices source text with `Program.range` must account
for comments and whitespace at both ends.

## Built-in Espree and scope types

Espree 11.1.0 and ESLint Scope 9.1.0 include built-in type definitions. They
replace the declarations previously provided by `@types/espree` and
`@types/eslint-scope`.

The built-in definitions are not identical to those declaration packages.
Typed rule, parser, or scope integrations may therefore require adjustments
even if runtime behavior is unchanged.

## Explicit color intent for formatters

The CLI conveys an explicit color choice through the context passed as the
second argument to a formatter's `format()` method:

| CLI option | Formatter context |
| --- | --- |
| `--color` | `color: true` |
| `--no-color` | `color: false` |

Custom formatters can inspect this context value to honor the explicit
styling choice rather than independently guessing whether to emit color.
