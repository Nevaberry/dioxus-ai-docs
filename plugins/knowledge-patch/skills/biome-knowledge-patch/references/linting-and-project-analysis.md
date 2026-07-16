# Linting and Project Analysis

Use this reference when enabling domains, configuring rule options, relying on
module-graph or type inference, or updating rule names and presets.

## Contents

- [Activate coherent linter domains](#activate-coherent-linter-domains)
- [Run project-domain analysis](#run-project-domain-analysis)
- [Resolve imports and dependencies](#resolve-imports-and-dependencies)
- [Enable compiler-independent type inference](#enable-compiler-independent-type-inference)
- [Configure naming and filenames](#configure-naming-and-filenames)
- [Configure hook and callback analysis](#configure-hook-and-callback-analysis)
- [Configure imports, overloads, and CSS exceptions](#configure-imports-overloads-and-css-exceptions)
- [Configure common rule exceptions](#configure-common-rule-exceptions)
- [Apply framework- and test-aware analysis](#apply-framework--and-test-aware-analysis)
- [Analyze CSS classes across languages](#analyze-css-classes-across-languages)
- [Apply package and database safeguards](#apply-package-and-database-safeguards)
- [Use CSS and JSON rules](#use-css-and-json-rules)
- [Account for expanded rule and fixer behavior](#account-for-expanded-rule-and-fixer-behavior)
- [Update deprecated, removed, and renamed rules](#update-deprecated-removed-and-renamed-rules)
- [Stable-rule promotions](#stable-rule-promotions)
- [New and nursery rule catalog](#new-and-nursery-rule-catalog)

## Activate coherent linter domains

Configure `linter.domains` with `"recommended"`, `"all"`, or `"none"`:

```json
{
  "linter": {
    "domains": {
      "react": "recommended",
      "test": "all",
      "solid": "none"
    }
  }
}
```

Available domains cover Drizzle, Next.js, Playwright, project analysis, Qwik,
React, Solid, generic tests, Turborepo, type inference, and Vue. Framework and
test domains can activate from matching package dependencies. Playwright and
test domains also provide their common globals.
This avoids separate `javascript.globals` entries for those environments.

`"recommended"` excludes nursery rules; `"all"` includes them. Enabling a
whole rule group does not implicitly enable React-, Qwik-, or other
domain-specific members. Such rules require a matching dependency, an explicit
domain, or explicit rule configuration.

Use domain names in `--only` and `--skip`. With `check` and `ci`, selectors may
also name individual rules, assist actions, groups, or domains.

## Run project-domain analysis

Enable the `project` domain to scan the module graph for rules such as:

- `noPrivateImports`
- `noUnresolvedImports`
- `noImportCycles`
- `noDeprecatedImports`

Only `noPrivateImports` is recommended; use `"project": "all"` or configure
the other rules individually.

```json
{ "linter": { "domains": { "project": "all" } } }
```

The default scanner discovers nested configurations. Enabling project rules
triggers a full scan of project files and `node_modules`; `files.includes`
cannot limit the `node_modules` scan. An ordinary `!` exclusion still permits a
dependency to be indexed. Use `!!` only when the scanner must neither traverse
nor index that path.

Rules that consult `package.json` use the manifest belonging to the relevant
package in a monorepo, keeping dependency analysis package-local.

## Resolve imports and dependencies

`noUnresolvedImports` understands `node:` built-ins, package `typings`, aliased
re-export chains, and namespace re-exports. Resolution prefers the most specific
overlapping package `exports` pattern.

`noUndeclaredDependencies` recognizes Node built-ins, Bun imports, Definitely
Typed type imports, dotted dependency names, self-package imports, and ignores
`@/` imports. Configure `bundleDependencies` when bundled packages should be
treated specially.

`noNodejsModules` ignores type-only imports and packages whose names collide
with Node modules. `useNodejsImportProtocol`, `useNodeAssertStrict`,
`noRestrictedImports`, and `noNodejsModules` do not inspect `declare module`
declarations.

## Enable compiler-independent type inference

The `types` domain enables type inference without requiring the TypeScript
compiler or an installed `typescript` package. Use `"types": "all"`; its
type-dependent rules are nursery and therefore are not selected by
`"recommended"`.

Core type-domain rules include:

- `noFloatingPromises`
- `noMisusedPromises`
- `noUnnecessaryConditions`
- `useAwaitThenable`
- `useExhaustiveSwitchCases`
- `useNullishCoalescing`
- `useArraySortCompare`
- `useArrayFind` (formerly `useFind`)
- `useRegexpExec`

Expect both project and type domains to increase lint time because they scan the
whole project.

Promise inference follows logical and conditional expressions, getters, call
signatures, comma operators, and async callbacks. Thus `noFloatingPromises` can
report an ignored promise-producing `map` callback:

```js
[1, 2, 3].map(async (x) => x + 1);
```

Type-aware rules infer `Record<K, V>` index signatures and follow re-exported
values for `useAwaitThenable`, `noFloatingPromises`, `noMisusedPromises`, and
`useArraySortCompare`.

## Configure naming and filenames

Use `useNamingConvention.options.conventions` for project-specific selectors,
regex transforms, and formats:

```json
{
  "linter": {
    "rules": {
      "style": {
        "useNamingConvention": {
          "level": "error",
          "options": {
            "conventions": [
              {
                "selector": {
                  "kind": "classMember",
                  "modifiers": ["private"]
                },
                "match": "_(.*)",
                "formats": ["camelCase"]
              }
            ]
          }
        }
      }
    }
  }
}
```

The rule accepts PascalCase local and top-level variables and ignores the casing
of destructured bindings.

`useFilenamingConvention` accepts unicase-only and numeric filenames, applies
configured formats to extensions, permits the leading `+` in SvelteKit and Vike
routes, and recognizes dynamic routes used by Next.js, SolidStart, Nuxt, and
Astro. Catch-all forms such as `[...slug].js` and `[[...slug]].js` are accepted
when the parameter is alphanumeric.

`useLiteralKeys` preserves computed `["__proto__"]` properties.

## Configure hook and callback analysis

`useExhaustiveDependencies`:

- understands React and Preact hooks;
- recognizes some dependencies that change every render;
- finds missing dependencies declared as function declarations;
- does not treat a recursive call as a missing dependency;
- detects duplicate dependencies;
- supports dependency-specific suppression comments;
- exposes `reportUnnecessaryDependencies`, defaulting to `true`;
- exposes `reportMissingDependenciesArray` for absent arrays.

`useHookAtTopLevel.ignore` exempts named `use*` utilities. The rule also reports
hooks at module scope and in non-hook, non-component functions or methods,
except function expressions.

Set `useIterableCallbackReturn.checkForEach: false` to skip `forEach` callbacks.
Set `useIterableCallbackReturn.allowImplicit` when an implicit callback return
is acceptable.

## Configure imports, overloads, and CSS exceptions

Set `useImportExtensions.suggestedExtensions` to control suggested suffixes.
Use `extensionMappings` to require a different output extension from the source,
such as TypeScript `ts` importing JavaScript `js`.

Use the current `useUnifiedTypeSignatures` rule, introduced under the singular
name `useUnifiedTypeSignature`. Its options
`ignoreDifferentlyNamedParameters` and `ignoreDifferentJsDoc` keep overloads
separate when parameter names or documentation differ.

Add `ignore` lists to `noUnknownProperty`, `noUnknownFunction`,
`noUnknownPseudoClass`, and `noUnknownPseudoElement` for project-specific CSS
extensions.

## Configure common rule exceptions

- `noBlankTarget.allowDomains` permits selected target-blank domains.
- `noConsole` can allow selected console methods.
- `useSelfClosingElements.ignoreHtmlElements` exempts named HTML elements.
- `noDoubleEquals.ignoreNull` defaults to allowing loose `null` comparisons;
  set it to `false` to report them.
- `noUnusedFunctionParameters.ignoreRestSiblings` permits deliberate omission
  through object-rest patterns.
- `noUnusedVariables.ignore` exempts selected names.
- `useNumericSeparators` supports numeric-grouping controls.
- `noImplicitCoercions.allowDoubleNegation` permits `!!value`.
- `useDomQuerySelector.ignore` exempts selected receiver identifiers.
- `noUndeclaredDependencies.bundleDependencies` configures treatment of
  bundled packages.

Example:

```json
{
  "linter": {
    "rules": {
      "a11y": {
        "noBlankTarget": {
          "level": "error",
          "options": { "allowDomains": ["example.com", "example.org"] }
        }
      },
      "correctness": {
        "noUnusedFunctionParameters": {
          "level": "error",
          "options": { "ignoreRestSiblings": true }
        }
      }
    }
  }
}
```

## Apply framework- and test-aware analysis

`noMisplacedAssertion` accepts assertions inside Testing Library `waitFor`,
method-based test APIs such as `test.each`, and Jest static helpers including
`expect.any`, `expect.objectContaining`, and `expect.extend`.

Playwright nursery coverage includes `noConditionalExpect`, `useExpect`,
`usePlaywrightValidDescribeCallback`, `noPlaywrightElementHandle`,
`noPlaywrightEval`, `noPlaywrightForceOption`, `noPlaywrightMissingAwait`,
`noPlaywrightNetworkidle`, `noPlaywrightPagePause`,
`noPlaywrightUselessAwait`, `noPlaywrightWaitForNavigation`,
`noPlaywrightWaitForSelector`, and `noPlaywrightWaitForTimeout`.
`noSkippedTests` absorbs Playwright-specific skip detection.

Assertion detection accepts Vitest `assert`, `expectTypeOf`, and `assertType`,
but does not treat asymmetric matchers or helpers such as `expect.extend()` as
standalone assertions.

`noUndeclaredVariables` recognizes Svelte 5 runes. `noUnusedVariables` treats a
Svelte `$store` template reference as use of its underlying binding and allows
`$bindable()` props written only in the script block.

The JavaScript analyzer recognizes TypeScript 5.5 and 5.6 globals.
`noUnusedVariables` checks non-global TypeScript declaration files but continues
to exclude global declaration files that contain no imports or exports.

`useVueValidVOn` accepts expressionless verb modifiers and the argument-less
object form. `noVueRefAsOperand` detects refs used without `.value`, and
`useVueScopedStyles` requires `scoped` or `module` on Vue SFC styles.

The React domain owns `noChildrenProp`, `noReactPropAssignments`,
`noDangerouslySetInnerHtml`, `noDangerouslySetInnerHtmlWithChildren`,
`useComponentExportOnlyModules`, and `noArrayIndexKey`. It recommends
`noChildrenProp`, both dangerously-set-inner-HTML rules, and `noArrayIndexKey`.

## Analyze CSS classes across languages

The nursery rules `noUnusedClasses` and `noUndeclaredClasses` use the module
graph across CSS, JSX, and HTML-like files. `noUnusedClasses` reports CSS classes
unused by markup. `noUndeclaredClasses` validates `class` and `className`
references against imported CSS and `<style>` definitions, including classes
exposed through `:global()`.

`noDuplicateClasses` is an assist that removes duplicates from HTML, JSX,
`clsx`, `cn`, and `cva` usage.

## Apply package and database safeguards

Configure `noUntrustedLicenses` with allowed or denied license identifiers and
optional OSI-approved or FSF-free requirements. `deny` takes precedence over
`allow`.

Use `noDrizzleUpdateWithoutWhere` and `noDrizzleDeleteWithoutWhere` to prevent
Drizzle operations that could update or delete an entire table.

`noRestrictedDependencies` uses the e18e replacement dataset to report a
dependency that has a native alternative or is deprecated or unnecessarily
heavy.

## Use CSS and JSON rules

Stable CSS coverage includes:

- `a11y/useGenericFontNames`;
- correctness checks for gradients, grid areas, `@import` placement, functions,
  media features, properties, units, and An+B selectors;
- suspicious checks for duplicate imports, font names, keyframe selectors,
  empty blocks, `!important` in keyframes, and shorthand overrides.

CSS nursery additions include `noDuplicateSelectors` within an at-rule context
and `useBaseline` for properties, values, at-rules, media conditions, functions,
and pseudo-selectors outside the configured Baseline tier.

JSON nursery additions include `noTopLevelLiterals`, which requires an object or
array root, and `noEmptyObjectKeys`, which rejects an empty-string key.
`noDuplicateObjectKeys` also analyzes JSON and JSONC.

## Account for expanded rule and fixer behavior

- `useOptionalChain` recognizes negated-OR and non-leading AND-chain patterns.
- `noNegationElse` handles inequality operators.
- `noSubstr` checks every expression context.
- `noProcessEnv` recognizes imports from `process` and `node:process` and reports
  dot or bracket access, including `process["env"]` and `env["NODE_ENV"]`.
- `noArrayIndexKey` checks an index anywhere in a JSX key template or binary
  expression.
- `organizeImports` sorts and merges bare exports and separates import and
  export chunks.
- `useConsistentMethodSignatures` has an unsafe conversion fix.
- `noUnsafeOptionalChaining` reports unsafe optional chains wrapped in
  TypeScript `as`, `satisfies`, type assertions, or instantiation expressions,
  including `new (value?.constructor as Constructor)()`.
- `noUnsafePlusOperands` reports unsafe operand types for both `+` and `+=`.

## Update deprecated, removed, and renamed rules

Replace deprecated paths:

| Deprecated | Replacement |
| --- | --- |
| `correctness/noInvalidNewBuiltin` | `correctness/noInvalidBuiltinInstantiation` |
| `style/useSingleCaseStatement` | `correctness/noSwitchDeclarations` |
| `suspicious/noConsoleLog` | `suspicious/noConsole` |

Use the corrected spelling `useConsistentBuiltinInstantiation`; the initially
published `useConsistentBuiltinInstatiation` spelling is obsolete.

Remove `useAnchorHref`; `useValidAnchor` covers its use case.

Use these current names after promotion:

| Former nursery name | Current stable name |
| --- | --- |
| `noFloatingClasses` | `noUnusedInstantiation` |
| `noMultiStr` | `noMultilineString` |
| `useFind` | `useArrayFind` |
| `useSpread` | `useSpreadOverApply` |

## Stable-rule promotions

Preserve the following promotion status when building presets or replacing
nursery-specific configuration.

Early general promotions include `complexity/noExcessiveNestedTestSuites`,
`complexity/noUselessTernary`, `correctness/useJsxKeyInIterable`,
`performance/noBarrelFile`, `performance/noReExportAll`,
`style/noNamespaceImport`, `style/useNodeAssertStrict`,
`suspicious/noDuplicateTestHooks`, `suspicious/noExportsInTest`,
`suspicious/noFocusedTests`, `suspicious/noSkippedTests`, and
`suspicious/noSuspiciousSemicolonInJsx` (`1.7-guide`).

Further promotions include `useImportRestrictions`, `noNodejsModules`,
`useArrayLiterals`, `noConstantMathMinMaxClamp`, and `noFlatMapIdentity`
(`1.8.0`).

The CSS/JavaScript promotion set includes `noLabelWithoutControl`,
`useFocusableInteractive`, `useSemanticElements`, `noUselessStringConcat`,
`noUselessUndefinedInitialization`, `useDateNow`, `noUndeclaredDependencies`,
`noInvalidBuiltinInstantiation`, `noUnusedFunctionParameters`,
`useImportExtensions`, `useTopLevelRegex`, `noDoneCallback`, `noYodaExpression`,
`useConsistentBuiltinInstantiation`, `useDefaultSwitchClause`,
`useExplicitLengthCheck`, `useThrowNewError`, `useThrowOnlyError`, `noConsole`,
`noEvolvingTypes`, `noMisplacedAssertion`, `noReactSpecificProps`,
`useErrorMessage`, and `useNumberToFixedDigitsArgument` (`1.9-guide`).

Framework and security promotions include
`suspicious/noNonNullAssertedOptionalChain`, `style/useReactFunctionComponents`,
`correctness/useImageSize`, `style/useConsistentTypeDefinitions`,
`correctness/useQwikClasslist`, and `security/noSecrets` (`2.3.0`).

Project and framework promotions include correctness rules
`noUnresolvedImports`, `noVueReservedProps`, `noVueReservedKeys`,
`noVueDataObjectDeclaration`, `noNextAsyncClientComponent`,
`noVueDuplicateKeys`, `noVueSetupPropsReactivityLoss`, `useQwikMethodUsage`, and
`useQwikValidLexicalScope`; suspicious rules `noImportCycles`,
`noDeprecatedImports`, `noReactForwardRef`, `noUnusedExpressions`,
`noEmptySource`, `useDeprecatedDate`, and `noDuplicateDependencies`; complexity
rules `noUselessUndefined`, `useMaxParams`, and `noUselessCatchBinding`; and
style rules `useConsistentArrowReturn` and `noJsxLiterals` (`2.4-guide`).

The broad stable promotion set moves seventy-three nursery rules
(`2.5-guide`) and is grouped as follows:

- Correctness: `noBeforeInteractiveScriptOutsideDocument`,
  `noUnusedInstantiation`, `useInlineScriptId`, `noVueVIfWithVFor`,
  `useVueValidVBind`, `useVueValidVElse`, `useVueValidVElseIf`,
  `useVueValidVHtml`, `useVueValidVIf`, `useVueValidVOn`, `useVueValidVText`,
  `useVueValidTemplateRoot`, `useVueValidVCloak`, `useVueValidVOnce`,
  `useVueValidVPre`, `useVueVForKey`, `noDuplicateAttributes`,
  `noDuplicateArgumentNames`, `noDuplicateInputFieldNames`,
  `noDuplicateVariableNames`, `noDuplicateEnumValueNames`, and
  `useLoneAnonymousOperation`.
- Suspicious: `noShadow`, `noUnnecessaryConditions`,
  `noParametersOnlyUsedInRecursion`, `noUnknownAttribute`,
  `useArraySortCompare`, `noForIn`, `noDuplicatedSpreadProps`,
  `noEqualsToNull`, `noProto`, `noUndeclaredEnvVars`, `noReturnAssign`,
  `noDuplicateEnumValues`, `noVueArrowFuncInWatch`, `noNestedPromises`,
  `noLeakedRender`, `noDeprecatedMediaType`, `noDuplicateGraphqlOperationName`,
  and `useRequiredScripts`.
- Style: `useVueMultiWordComponentNames`, `useVueDefineMacrosOrder`,
  `noIncrementDecrement`, `noContinue`, `useSpreadOverApply`, `noTernary`,
  `noMultilineString`, `noMultiAssign`, `noExcessiveClassesPerFile`,
  `noExcessiveLinesPerFile`, `noVueOptionsApi`, `useErrorCause`,
  `useConsistentEnumValueType`, `useConsistentMethodSignatures`,
  `useGlobalThis`, `useDestructuring`, `useVueHyphenatedAttributes`,
  `useVueConsistentVBindStyle`, `useVueConsistentVOnStyle`, `noHexColors`,
  `useConsistentGraphqlDescriptions`, `noRootType`,
  `useLoneExecutableDefinition`, and `useInputName`.
- Complexity: `useArrayFind`, `noRedundantDefaultExport`, `noUselessReturn`, and
  `noDivRegex`.
- Performance: `noSyncScripts`, `noJsxPropsBind`, and `useVueVapor`.
- Security: `noScriptUrl`.
- A11y: `noAmbiguousAnchorText`.

## New and nursery rule catalog

Retain these additions when a project explicitly selects nursery or configures
rules one by one.

General nursery additions include `noConstantMathMinMaxClamp`, `noDoneCallback`,
`noDuplicateElseIf`, `noEvolvingTypes`, `noFlatMapIdentity`, and
`noMisplacedAssertion` (`1.7-guide`).

Additional JavaScript rules include `noUselessUndefinedInitialization`,
`noReactSpecificProps`, `noUselessStringConcat`, `useArrayLiterals`,
`useConsistentBuiltinInstantiation`, `useDefaultSwitchClause`, and
`useExplicitLengthCheck` (`1.7.0`).

JavaScript and accessibility additions include `useDateNow`, `useErrorMessage`,
`useThrowOnlyError`, `useImportExtensions`,
`useNumberToFixedDigitsArgument`, `useThrowNewError`, `useTopLevelRegex`,
`noYodaExpression`, `noUnusedFunctionParameters`, `useSemanticElements`,
`noSubstr`, `useConsistentCurlyBraces`, `useValidAutocomplete`,
`noShorthandPropertyOverrides`, `useDeprecatedReason`, and
`noExportedImports` (`1.8.0`).

CSS nursery additions include `noCssEmptyBlock`, `noDuplicateAtImportRules`,
`noDuplicateFontNames`, `noDuplicateSelectorsKeyframeBlock`,
`noImportantInKeyframe`, `noInvalidPositionAtImportRule`, `noUnknownFunction`,
`noUnknownMediaFeatureName`, `noUnknownProperty`, `noUnknownPseudoElement`,
`noUnknownPseudoClass`, `noUnknownUnit`, `noUnmatchableAnbSelector`, and
`useGenericFontNames` (`1.8.0`).

Cross-language nursery additions include `noCommonJs`,
`noDuplicateCustomProperties`, `noDynamicNamespaceImportAccess`, `noEnum`,
`noIrregularWhitespace`, `noRestrictedTypes`, `noSecrets`,
`noUselessEscapeInRegex`, `noValueAtRule`,
`useConsistentMemberAccessibility`, and `useTrimStartEnd` (`1.9-guide`).

The extended rule set includes `useAriaPropsSupportedByRole`, `useStrictMode`,
`noProcessEnv`, `noMissingVarFunction`, `useComponentExportOnlyModules`,
`noDescendingSpecificity`, `noNestedTernary`, `noTemplateCurlyInString`,
`noOctalEscape`, `useGuardForIn`, `noDocumentCookie`,
`noDocumentImportInPage`, `noDuplicateProperties`, `noHeadElement`,
`noHeadImportInDocument`, `noImgElement`, `noUnknownTypeSelector`, `useAtIndex`,
`noUselessStringRaw`, `useCollapsedIf`, `useGoogleFontDisplay`, and
`useExportsLast` (`1.9.0`).

Further general rules include `noAlert`, `noImplicitCoercion`, `noMagicNumbers`,
`noUnassignedVariables`, `useReadonlyClassProperties`, and
`useUnifiedTypeSignatures` (`2.1.0`).

JavaScript nursery additions include `noImpliedEval`, `noUnsafePlusOperands`,
`useImportsFirst`, `useNullishCoalescing`, `useNamedCaptureGroup`,
`useUnicodeRegex`, and `useArraySome`. `useArraySome` also recognizes existence
checks built from `find`, `findLast`, and ES2025 iterator helpers (`2.4.0`).

Framework additions include `noInlineStyles` for HTML style attributes, JSX
style props, and `React.createElement`; `useVueScopedStyles`; and
`noVueRefAsOperand` (`2.4.0`).

Package and database additions include `noUntrustedLicenses`,
`noDrizzleUpdateWithoutWhere`, and `noDrizzleDeleteWithoutWhere` (`2.4.0`). CSS
adds `noDuplicateSelectors` and `useBaseline`; JSON adds `noTopLevelLiterals`
and `noEmptyObjectKeys`.

Cross-language CSS analysis adds `noUnusedClasses` and `noUndeclaredClasses`,
and dependency analysis adds `noRestrictedDependencies` (`2.5-guide`).

Coverage IDs: `1.7-guide`, `1.7.0`, `1.8.0`, `1.9-guide`, `1.9.0`,
`2.0-guides`, `2.0.0`, `2.1.0`, `2.3.0`, `2.4-guide`, `2.4.0`, `2.5-guide`,
`2.5.0`.
