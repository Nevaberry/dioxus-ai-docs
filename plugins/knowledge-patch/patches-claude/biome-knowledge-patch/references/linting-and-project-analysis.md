# Linting and Project Analysis

## Configure rules and severity

At group level, `"all": false` disables that group's recommended rules even
when top-level `recommended` is true or omitted (since `1.7.0`). A rule without
options can use object form with only `level`; it does not need
`"options": null`.

```json
{
  "linter": {
    "rules": {
      "recommended": true,
      "style": { "all": false }
    }
  }
}
```

Rules accept `"info"` severity (since `1.8.0`). Informational diagnostics have
no error code and are unaffected by `--error-on-warnings`. Object-form rules
can set `fix` to `none`, `safe`, or `unsafe`; since `2.5.1`, every object-form
rule must include `level` or configuration fails.

`linter.rules.preset` replaces deprecated `linter.rules.recommended` (since
`2.5-guide`). `"all"` selects every stable rule but excludes nursery;
`"recommended"` preserves the recommended selection.

## Enable linter domains

`linter.domains` enables coherent dependency-aware rule sets (since
`2.0-guides`). Values are `"recommended"`, `"all"`, and `"none"`.
Recommended excludes nursery; all includes it. Domains cover Drizzle, Next.js,
Playwright, project analysis, Qwik, React, Solid, generic tests, Turborepo,
types, and Vue. Supported framework and test domains activate when their
matching package dependencies are declared.

```json
{
  "linter": {
    "domains": { "react": "recommended", "test": "all", "solid": "none" }
  }
}
```

The Playwright and test domains provide their common globals. The test domain
also supplies Mocha `context`, `run`, `setup`, `specify`, `suite`,
`suiteSetup`, `suiteTeardown`, `teardown`, `xcontext`, `xdescribe`, `xit`, and
`xspecify` (since `2.4.0`).

Enabling a whole rule group does not enable that group's React, Qwik, or other
domain-specific rules (since `2.4.0`). A matching dependency, explicit domain,
or explicit rule is required.

In the React domain, `noChildrenProp`, `noReactPropAssignments`,
`noDangerouslySetInnerHtml`, `noDangerouslySetInnerHtmlWithChildren`,
`useComponentExportOnlyModules`, and `noArrayIndexKey` became domain members in
`2.3.0`. Recommended members are `noChildrenProp`, both dangerous-inner-HTML
rules, and `noArrayIndexKey`.

## Project and type-aware analysis

The `project` domain scans the module graph. It includes `noPrivateImports`,
`noUnresolvedImports`, `noImportCycles`, and `noDeprecatedImports`; only
`noPrivateImports` is recommended, so the others need `"project": "all"` or
individual configuration (since `2.0-guides`).

The `types` domain adds compiler-independent type inference. It initially
included `noFloatingPromises`, `noMisusedPromises`, `noUnnecessaryConditions`,
`useAwaitThenable`, `useExhaustiveSwitchCases`, and `useNullishCoalescing`.
These are nursery rules and require `"types": "all"`, not
`"recommended"`. `useArraySortCompare`, `useFind`, and `useRegexpExec` joined
the domain in `2.4-guide`.

```json
{ "linter": { "domains": { "project": "all", "types": "all" } } }
```

Type inference does not require the `typescript` package (since `2.0.0`). The
ordinary scanner discovers nested configurations; project rules trigger a full
scan of project files and `node_modules`, which `files.includes` cannot limit.
Both project and type domains can materially increase lint time. An ordinary
`!` exclusion can still be indexed as a dependency; use `!!` only to prevent
all reading of a subtree.

Rules consulting `package.json` use the manifest for the relevant monorepo
package (since `2.0.0`). Resolution now prefers the most specific overlapping
package `exports` pattern, and `noUnresolvedImports` understands `node:`
built-ins, package `typings`, aliased re-export chains, and namespace
re-exports (since `2.4.0`).

Type-aware rules infer `Record<K, V>` index signatures and follow re-exported
values for `useAwaitThenable`, `noFloatingPromises`, `noMisusedPromises`, and
`useArraySortCompare` (since `2.4.0`). Promise inference also tracks logical
and conditional expressions, getters, call signatures, comma operators, and
async callback results such as `Array.prototype.map` (since `2.1.0`).

```js
[1, 2, 3].map(async (x) => x + 1);
```

## Hook and assertion analysis

`useExhaustiveDependencies` supports React and Preact hooks, recognizes
dependencies that change each render, finds missing dependencies declared as
function declarations, and does not treat recursive calls as missing (changes
across `1.7-guide` and `1.7.0`). It reports duplicates and permits
dependency-specific suppressions (since `1.8.0`).

Options added in `1.9.0` are `reportUnnecessaryDependencies` (default `true`)
and `reportMissingDependenciesArray`.

`useHookAtTopLevel.ignore` exempts named `use*` utilities (since
`2.4-guide`). The rule also detects hooks at module scope and in non-hook,
non-component functions or methods, except function expressions.

`noMisplacedAssertion` accepts Testing Library `waitFor`, method-based test APIs
such as `test.each`, and Jest static helpers such as `expect.any`,
`expect.objectContaining`, and `expect.extend` (since `1.7.0`). Assertion
detection later accepted Vitest `assert`, `expectTypeOf`, and `assertType`, but
rejected asymmetric matchers and helpers such as `expect.extend()` as
standalone assertions (since `2.4.0`).

## Dependency and framework-aware behavior

`noUndeclaredDependencies` recognizes Node built-ins, Bun imports, Definitely
Typed imports, dotted dependency names, self-package imports, and ignores `@/`
imports (since `1.9.0`). `noNodejsModules` ignores type-only imports and
packages whose names collide with Node modules. `noUndeclaredVariables`
recognizes Svelte 5 runes, while `noUnusedVariables` analyzes non-global
TypeScript declaration files; global declarations without imports/exports stay
excluded.

`useFilenamingConvention` accepts unicase-only and numeric filenames, applies
formats to extensions, and recognizes Next.js, SolidStart, Nuxt, and Astro
dynamic routes (since `1.9.0`). Catch-all `[...slug].js` and
`[[...slug]].js` are allowed when `slug` is alphanumeric. Earlier compatibility
also permits the leading `+` used by SvelteKit and Vike (since `1.7.0`).

`useNamingConvention` accepts PascalCase local/top-level variables and ignores
destructured-binding casing (since `1.7.0`). Its `options.conventions` supports
selectors, regex matching, and allowed formats for custom policies (since
`1.8.0`).

```json
{
  "linter": {
    "rules": {
      "style": {
        "useNamingConvention": {
          "level": "error",
          "options": {
            "conventions": [{
              "selector": { "kind": "classMember", "modifiers": ["private"] },
              "match": "_(.*)",
              "formats": ["camelCase"]
            }]
          }
        }
      }
    }
  }
}
```

## Rule option changes

- `useImportExtensions.suggestedExtensions` was added in `1.8.0`;
  `extensionMappings` can map source `ts` to required import `js` (since
  `2.4-guide`).
- `useSortedClasses` sorts known and dynamic Tailwind variants and puts
  arbitrary variants after known ones, but does not support screen variants
  such as `sm:`, `max-md:`, or `min-lg:` (since `1.8.0`).
- `noBlankTarget.allowDomains`, selected-call allowances for `noConsole`, and
  `useSelfClosingElements.ignoreHtmlElements` arrived in `1.9.0`.
- `noDoubleEquals.ignoreNull` defaults to allowing loose comparison with
  `null`; set it to `false` to report it (since `1.9.0`).
- `noUnusedFunctionParameters.ignoreRestSiblings` permits intentional sibling
  omission in object-rest parameter patterns (since `2.1.0`).
- `useIterableCallbackReturn.checkForEach: false` skips `forEach` callbacks;
  `useUnifiedTypeSignatures` gained `ignoreDifferentlyNamedParameters` and
  `ignoreDifferentJsDoc` (since `2.4-guide`).
- `noUnknownProperty`, `noUnknownFunction`, `noUnknownPseudoClass`, and
  `noUnknownPseudoElement` gained ignore lists (since `2.4-guide`).
- `noUnusedVariables.ignore`, `useIterableCallbackReturn.allowImplicit`,
  numeric-grouping controls for `useNumericSeparators`,
  `noUndeclaredDependencies.bundleDependencies`, and
  `noImplicitCoercions.allowDoubleNegation` arrived in `2.5-guide`.
- `useDomQuerySelector.ignore` exempts named receiver identifiers (since
  `2.5.0`).

## Rule behavior and fixer changes

The `1.7.0` series refined several rules: `useLiteralKeys` preserves computed
`["__proto__"]`; `useNodejsImportProtocol`, `useNodeAssertStrict`,
`noRestrictedImports`, and `noNodejsModules` ignore `declare module`;
`noMisplacedAssertion` recognizes async/test helper contexts; and
`useExhaustiveDependencies` improves function and recursion handling.

Changes in `2.4.0` include:

- `useOptionalChain` recognizes negated-OR and non-leading AND chains.
- `noNegationElse` covers inequality operators; `noSubstr` checks every
  expression context.
- `noProcessEnv` recognizes imports from `process` and `node:process`.
- `noArrayIndexKey` detects indexes anywhere in JSX-key template or binary
  expressions.
- `useConsistentMethodSignatures` has an unsafe conversion fix.

`2.5.0` further makes `noUnsafeOptionalChaining` detect optional chains wrapped
in TypeScript `as`, `satisfies`, type assertions, or instantiation expressions.
`noProcessEnv` detects bracket access such as `process["env"]` and
`env["NODE_ENV"]` when `env` comes from `node:process`.

## Rules introduced and promoted in the 1.x series

The `1.7-guide` nursery added `noConstantMathMinMaxClamp`, `noDoneCallback`,
`noDuplicateElseIf`, `noEvolvingTypes`, `noFlatMapIdentity`, and
`noMisplacedAssertion`. Nursery rules are outside semantic-versioning
guarantees.

The stable promotions in `1.7-guide` were
`complexity/noExcessiveNestedTestSuites`, `complexity/noUselessTernary`,
`correctness/useJsxKeyInIterable`, `performance/noBarrelFile`,
`performance/noReExportAll`, `style/noNamespaceImport`,
`style/useNodeAssertStrict`, `suspicious/noDuplicateTestHooks`,
`suspicious/noExportsInTest`, `suspicious/noFocusedTests`,
`suspicious/noSkippedTests`, and `suspicious/noSuspiciousSemicolonInJsx`.

The `1.7.0` series added `noUselessUndefinedInitialization`,
`noReactSpecificProps`, `noUselessStringConcat`, `useArrayLiterals`,
`useConsistentBuiltinInstantiation`, `useDefaultSwitchClause`, and
`useExplicitLengthCheck`. The final spelling is
`useConsistentBuiltinInstantiation`, correcting the initially published
`Instatiation` spelling.

Stable promotions in `1.8.0` were `useImportRestrictions`, `noNodejsModules`,
`useArrayLiterals`, `noConstantMathMinMaxClamp`, and `noFlatMapIdentity`.

JavaScript and accessibility nursery additions in `1.8.0` were `useDateNow`,
`useErrorMessage`, `useThrowOnlyError`, `useImportExtensions`,
`useNumberToFixedDigitsArgument`, `useThrowNewError`, `useTopLevelRegex`,
`noYodaExpression`, `noUnusedFunctionParameters`, `useSemanticElements`,
`noSubstr`, `useConsistentCurlyBraces`, `useValidAutocomplete`,
`noShorthandPropertyOverrides`, `useDeprecatedReason`, and
`noExportedImports`.

CSS nursery additions in `1.8.0` were `noCssEmptyBlock`,
`noDuplicateAtImportRules`, `noDuplicateFontNames`,
`noDuplicateSelectorsKeyframeBlock`, `noImportantInKeyframe`,
`noInvalidPositionAtImportRule`, `noUnknownFunction`, `noUnknownMediaFeatureName`,
`noUnknownProperty`, `noUnknownPseudoElement`, `noUnknownPseudoClass`,
`noUnknownUnit`, `noUnmatchableAnbSelector`, and `useGenericFontNames`.

Stable promotions in `1.9-guide` were `noLabelWithoutControl`,
`useFocusableInteractive`, `useSemanticElements`, `noUselessStringConcat`,
`noUselessUndefinedInitialization`, `useDateNow`, `noUndeclaredDependencies`,
`noInvalidBuiltinInstantiation`, `noUnusedFunctionParameters`,
`useImportExtensions`, `useTopLevelRegex`, `noDoneCallback`, `noYodaExpression`,
`useConsistentBuiltinInstantiation`, `useDefaultSwitchClause`,
`useExplicitLengthCheck`, `useThrowNewError`, `useThrowOnlyError`, `noConsole`,
`noEvolvingTypes`, `noMisplacedAssertion`, `noReactSpecificProps`,
`useErrorMessage`, and `useNumberToFixedDigitsArgument`.

The `1.9-guide` nursery added `noCommonJs`, `noDuplicateCustomProperties`,
`noDynamicNamespaceImportAccess`, `noEnum`, `noIrregularWhitespace`,
`noRestrictedTypes`, `noSecrets`, `noUselessEscapeInRegex`, `noValueAtRule`,
`useConsistentMemberAccessibility`, and `useTrimStartEnd`.

Additional `1.9.0` series rules were `useAriaPropsSupportedByRole`,
`useStrictMode`, `noProcessEnv`, `noMissingVarFunction`,
`useComponentExportOnlyModules`, `noDescendingSpecificity`,
`noNestedTernary`, `noTemplateCurlyInString`, `noOctalEscape`, `useGuardForIn`,
`noDocumentCookie`, `noDocumentImportInPage`, `noDuplicateProperties`,
`noHeadElement`, `noHeadImportInDocument`, `noImgElement`,
`noUnknownTypeSelector`, `useAtIndex`, `noUselessStringRaw`, `useCollapsedIf`,
`useGoogleFontDisplay`, and `useExportsLast`.

## Rules introduced and promoted in the 2.x series

`2.1.0` added `noAlert`, `noImplicitCoercion`, `noMagicNumbers`,
`noUnassignedVariables`, `useReadonlyClassProperties`, and
`useUnifiedTypeSignature`.

Stable promotions in `2.3.0` were
`suspicious/noNonNullAssertedOptionalChain`, `style/useReactFunctionComponents`,
`correctness/useImageSize`, `style/useConsistentTypeDefinitions`,
`correctness/useQwikClasslist`, and `security/noSecrets`.

Stable promotions in `2.4-guide` were:

- Correctness: `noUnresolvedImports`, `noVueReservedProps`,
  `noVueReservedKeys`, `noVueDataObjectDeclaration`,
  `noNextAsyncClientComponent`, `noVueDuplicateKeys`,
  `noVueSetupPropsReactivityLoss`, `useQwikMethodUsage`, and
  `useQwikValidLexicalScope`.
- Suspicious: `noImportCycles`, `noDeprecatedImports`, `noReactForwardRef`,
  `noUnusedExpressions`, `noEmptySource`, `useDeprecatedDate`, and
  `noDuplicateDependencies`.
- Complexity: `noUselessUndefined`, `useMaxParams`, and
  `noUselessCatchBinding`.
- Style: `useConsistentArrowReturn` and `noJsxLiterals`.

The `2.4.0` Playwright nursery added `noConditionalExpect`, `useExpect`,
`usePlaywrightValidDescribeCallback`, `noPlaywrightElementHandle`,
`noPlaywrightEval`, `noPlaywrightForceOption`, `noPlaywrightMissingAwait`,
`noPlaywrightNetworkidle`, `noPlaywrightPagePause`,
`noPlaywrightUselessAwait`, `noPlaywrightWaitForNavigation`,
`noPlaywrightWaitForSelector`, and `noPlaywrightWaitForTimeout`.
`noSkippedTests` absorbed Playwright-specific skip detection.

JavaScript nursery additions in `2.4.0` were `noImpliedEval`,
`noUnsafePlusOperands`, `useImportsFirst`, `useNullishCoalescing`,
`useNamedCaptureGroup`, `useUnicodeRegex`, and `useArraySome`. `useArraySome`
also recognizes existence checks using `find`, `findLast`, and ES2025 iterator
helpers.

Framework and safety additions in `2.4.0` include `noInlineStyles`,
`useVueScopedStyles`, `noVueRefAsOperand`, `noUntrustedLicenses`,
`noDrizzleUpdateWithoutWhere`, and `noDrizzleDeleteWithoutWhere`.
`noUntrustedLicenses` can allow/deny license identifiers and require OSI or
FSF-free status; deny wins over allow. The Drizzle rules guard full-table
updates and deletes.

The `2.4.0` CSS nursery added `noDuplicateSelectors` and `useBaseline`; its JSON
nursery added `noTopLevelLiterals` and `noEmptyObjectKeys`.

## Cross-language and dependency rules

`noUnusedClasses` and `noUndeclaredClasses` use the module graph across CSS,
JSX, and HTML-like files (since `2.5-guide`). The former reports CSS classes
unused by markup; the latter validates `class`/`className` against imported CSS
and `<style>` definitions, including classes exposed through `:global()`.

`noRestrictedDependencies` uses the e18e replacement dataset to report
dependencies with native alternatives or that are deprecated or unnecessarily
heavy (since `2.5-guide`).

## Stable promotions in 2.5

The `2.5-guide` promoted 73 nursery rules and renamed four of them. The stable
set is:

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
  `noLeakedRender`, `noDeprecatedMediaType`,
  `noDuplicateGraphqlOperationName`, and `useRequiredScripts`.
- Style: `useVueMultiWordComponentNames`, `useVueDefineMacrosOrder`,
  `noIncrementDecrement`, `noContinue`, `useSpreadOverApply`, `noTernary`,
  `noMultilineString`, `noMultiAssign`, `noExcessiveClassesPerFile`,
  `noExcessiveLinesPerFile`, `noVueOptionsApi`, `useErrorCause`,
  `useConsistentEnumValueType`, `useConsistentMethodSignatures`,
  `useGlobalThis`, `useDestructuring`, `useVueHyphenatedAttributes`,
  `useVueConsistentVBindStyle`, `useVueConsistentVOnStyle`, `noHexColors`,
  `useConsistentGraphqlDescriptions`, `noRootType`,
  `useLoneExecutableDefinition`, and `useInputName`.
- Complexity: `useArrayFind`, `noRedundantDefaultExport`, `noUselessReturn`,
  and `noDivRegex`.
- Performance: `noSyncScripts`, `noJsxPropsBind`, and `useVueVapor`.
- Security: `noScriptUrl`.
- Accessibility: `noAmbiguousAnchorText`.

The renamed stable paths are `noUnusedInstantiation` (formerly
`noFloatingClasses`), `noMultilineString` (formerly `noMultiStr`),
`useArrayFind` (formerly `useFind`), and `useSpreadOverApply` (formerly
`useSpread`).
