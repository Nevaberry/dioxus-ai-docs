# Linting and Project Analysis

## Domains and enablement

### Domain presets (2.0-guides)

`linter.domains` enables coherent rule sets with `"recommended"`, `"all"`, or
`"none"`. Recommended excludes nursery rules; all includes them. Available
domains cover Drizzle, Next.js, Playwright, project analysis, Qwik, React,
Solid, generic tests, Turborepo, type inference, and Vue. Framework and test
domains activate when their matching package dependencies are declared.

```json
{
  "linter": {
    "domains": { "react": "recommended", "test": "all", "solid": "none" }
  }
}
```

Playwright and test domains also declare common test globals, avoiding separate
`javascript.globals` configuration.

Enabling an entire rule group does not enable that group's React-, Qwik-, or
other domain-specific rules unless a matching dependency, explicit domain, or
explicit rule configuration enables them (2.4.0).

### Project domain (2.0-guides)

The `project` domain scans the module graph for `noPrivateImports`,
`noUnresolvedImports`, `noImportCycles`, and `noDeprecatedImports`. Only
`noPrivateImports` is recommended; enable `"project": "all"` or configure the
others individually.

### Types domain (2.0-guides)

The `types` domain enables inference for `noFloatingPromises`,
`noMisusedPromises`, `noUnnecessaryConditions`, `useAwaitThenable`,
`useExhaustiveSwitchCases`, and `useNullishCoalescing`. These are nursery rules,
so use `"types": "all"`, not `"recommended"`.

```json
{ "linter": { "domains": { "project": "all", "types": "all" } } }
```

The domain later also classifies `useArraySortCompare`, `useFind`, and
`useRegexpExec` as type-dependent (2.4-guide).

Both domains scan the whole project and can materially increase lint time. A
normal `!` exclusion can still permit dependency indexing; use `!!` when no
module or type information should be read.

## Scanner, resolution, and type inference

### Compiler-independent inference (2.0.0)

Biome inference does not rely on the TypeScript compiler, so type-aware linting
does not require the `typescript` package. By default, the scanner only
discovers nested configurations. Project rules trigger a full scan of project
files and `node_modules`; `files.includes` cannot limit the latter.

Package-aware rules use the `package.json` belonging to the relevant monorepo
package (2.0.0).

### Promise inference (2.1.0)

Type analysis tracks promises through logical and conditional expressions,
getters, call signatures, and comma operators. `noFloatingPromises` also
catches unhandled promises from callbacks such as `Array.prototype.map`.

```js
[1, 2, 3].map(async (x) => x + 1);
```

### Module resolution and cross-module types (2.4.0)

Resolution prefers the most specific overlapping package `exports` pattern.
`noUnresolvedImports` understands `node:` built-ins, package `typings`, aliased
re-export chains, and namespace re-exports.

Type-aware rules infer `Record<K, V>` index signatures and follow re-exported
values for `useAwaitThenable`, `noFloatingPromises`, `noMisusedPromises`, and
`useArraySortCompare`.

## Rule configuration and options

### Group and object form (1.7.0)

At group level, `"all": false` disables that group's recommended rules even
when top-level `recommended` is true or omitted. A rule without options can use
object form with `level` alone; `"options": null` is unnecessary.

As of 2.5.1, object-form rule configuration must include `level`; omission is a
configuration error.

### Severity and fixes (1.8.0)

Rules accept `"info"`; informational diagnostics have no error code and ignore
`--error-on-warnings`. Object-form `fix` accepts `none`, `safe`, or `unsafe` to
disable actions or override their applicability.

### Custom naming conventions (1.8.0)

`useNamingConvention.options.conventions` combines selectors, regex matching,
and formats for project-specific naming.

```json
{ "linter": { "rules": { "style": { "useNamingConvention": { "level": "error", "options": { "conventions": [{ "selector": { "kind": "classMember", "modifiers": ["private"] }, "match": "_(.*)", "formats": ["camelCase"] }] } } } } } }
```

### Exhaustive dependency options

`useExhaustiveDependencies.reportUnnecessaryDependencies` defaults to `true`
and controls declared-but-unused dependency reports.
`reportMissingDependenciesArray` controls absent-array reports (1.9.0).

### Rule option additions (1.9.0)

- `noBlankTarget.allowDomains` allows selected domains.
- `noConsole` can allow selected console calls.
- `useSelfClosingElements.ignoreHtmlElements` skips selected elements.
- `noDoubleEquals.ignoreNull` defaults to allowing loose `null` comparisons;
  set it to `false` to report them.

```json
{ "linter": { "rules": { "a11y": { "noBlankTarget": { "level": "error", "options": { "allowDomains": ["example.com", "example.org"] } } } } } }
```

### Rest sibling option (2.1.0)

`noUnusedFunctionParameters.ignoreRestSiblings` permits object-rest omission
patterns without reporting the deliberately unused sibling binding.

```json
{
  "linter": {
    "rules": {
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

### Hook, import, callback, overload, and CSS options (2.4-guide)

- `useHookAtTopLevel.ignore` exempts named `use*` utilities. The rule also
  detects module-scope hooks and hooks in non-hook, non-component functions or
  methods, except function expressions.
- `useIterableCallbackReturn.checkForEach: false` skips `forEach` callbacks.
- `useImportExtensions.extensionMappings` maps source extensions such as `ts`
  to required import extensions such as `js`.
- `useUnifiedTypeSignatures` accepts `ignoreDifferentlyNamedParameters` and
  `ignoreDifferentJsDoc`.
- `noUnknownProperty`, `noUnknownFunction`, `noUnknownPseudoClass`, and
  `noUnknownPseudoElement` accept `ignore` lists.

`useSortedKeys.groupByNesting` groups simple values before multiline arrays and
objects and sorts within those groups.

### Further options (2.5-guide)

Rule configuration adds `noUnusedVariables.ignore`,
`useIterableCallbackReturn.allowImplicit`, numeric-grouping controls for
`useNumericSeparators`, `noUndeclaredDependencies.bundleDependencies`, and
`noImplicitCoercions.allowDoubleNegation`.

`useDomQuerySelector.ignore` skips configured receiver identifiers (2.5.0).

## Framework- and dependency-aware behavior

### Hooks and tests (1.7.0)

`useExhaustiveDependencies` recognizes some dependencies that change every
render, finds missing dependencies declared as function declarations, and does
not treat a recursive call as missing. It understands Preact as well as React
(1.7-guide).

`noMisplacedAssertion` accepts assertions in Testing Library `waitFor`,
method-based APIs such as `test.each`, and Jest static helpers including
`expect.any`, `expect.objectContaining`, and `expect.extend`.

### Naming and declarations (1.7.0)

`useFilenamingConvention` permits the leading `+` used by SvelteKit and Vike.
`useNamingConvention` accepts PascalCase local and top-level variables and
ignores destructured-binding casing. `useLiteralKeys` preserves computed
`["__proto__"]` properties.

`useNodejsImportProtocol`, `useNodeAssertStrict`, `noRestrictedImports`, and
`noNodejsModules` do not inspect `declare module` declarations.

### Dependency and framework analysis (1.9.0)

The JavaScript linter recognizes TypeScript 5.5 and 5.6 globals.
`noUnusedVariables` checks non-global TypeScript declaration files; global
declaration files without imports or exports remain excluded.

`noUndeclaredDependencies` recognizes Node built-ins, Bun imports, Definitely
Typed type imports, dotted dependency names, and self-package imports, and
ignores `@/` imports. `noNodejsModules` ignores type-only imports and packages
whose names collide with Node modules.

`noUndeclaredVariables` recognizes Svelte 5 runes in `.svelte`, `.svelte.js`,
and `.svelte.ts`. Vue SFC scripts with `lang="jsx"` parse as JSX.

`useFilenamingConvention` accepts unicase-only and numeric filenames, applies
formats to extensions, and recognizes dynamic routes used by Next.js,
SolidStart, Nuxt, and Astro. Catch-all names such as `[...slug].js` and
`[[...slug]].js` are accepted when `slug` is alphanumeric.

### React domain membership (2.3.0)

`noChildrenProp`, `noReactPropAssignments`, `noDangerouslySetInnerHtml`,
`noDangerouslySetInnerHtmlWithChildren`, `useComponentExportOnlyModules`, and
`noArrayIndexKey` belong to the `react` domain. They require explicit domain
enablement or a nearby React dependency. Recommended members are
`noChildrenProp`, both `noDangerouslySetInnerHtml` rules, and
`noArrayIndexKey`.

### Assertion and Playwright analysis (2.4.0)

`noSkippedTests` absorbs Playwright-specific skip detection. Assertion
detection accepts Vitest `assert`, `expectTypeOf`, and `assertType`, but rejects
asymmetric matchers and helpers such as `expect.extend()` as standalone
assertions.

### Expanded existing-rule coverage (2.4.0)

- `useOptionalChain` recognizes negated-OR and non-leading AND-chain patterns.
- `noNegationElse` covers inequality operators.
- `noSubstr` checks every expression context.
- `noProcessEnv` recognizes imports from `process` and `node:process`.
- `noArrayIndexKey` finds indices anywhere in JSX-key template or binary
  expressions.
- `useConsistentMethodSignatures` gains an unsafe conversion fix.

### Svelte, Vue, Astro, and process environment (2.5.0)

`noUnusedVariables` treats a Svelte `$store` template reference as use of the
underlying binding and permits `$bindable()` props only written in script.
`noUnsafeOptionalChaining` catches unsafe optional chains wrapped by TypeScript
`as`, `satisfies`, type assertions, or instantiation expressions, including
`new (value?.constructor as Constructor)()`.

`useVueValidVOn` accepts handlerless verb modifiers and the argument-less object
form. Astro shorthand attributes parse correctly. `noProcessEnv` checks bracket
access such as `process["env"]` and `env["NODE_ENV"]` when `env` comes from
`node:process`.

## Cross-language and dependency rules

`noUnusedClasses` and `noUndeclaredClasses` are nursery rules that use the
module graph across CSS, JSX, and HTML-like files. The former reports CSS
classes unused by markup. The latter checks `class` and `className` references
against imported CSS and `<style>` definitions, including `:global()` classes
(2.5-guide).

`noRestrictedDependencies` uses the e18e replacement dataset to report
dependencies with a native alternative or considered deprecated or
unnecessarily heavy (2.5-guide).

The e18e rule source maps to `useAtIndex`, `useExponentiationOperator`,
`noPrototypeBuiltins`, `useDateNow`, `useSpread`, and `useObjectSpread`
(2.4-guide).

## Rule additions

### Early nursery additions (1.7-guide)

`noConstantMathMinMaxClamp`, `noDoneCallback`, `noDuplicateElseIf`,
`noEvolvingTypes`, `noFlatMapIdentity`, and `noMisplacedAssertion` enter the
nursery. Nursery rules are exempt from semantic-versioning guarantees.

### Further 1.7 rules (1.7.0)

The series adds `noUselessUndefinedInitialization` and nursery rules
`noReactSpecificProps`, `noUselessStringConcat`, `useArrayLiterals`,
`useConsistentBuiltinInstantiation`, `useDefaultSwitchClause`, and
`useExplicitLengthCheck`. The final spelling is
`useConsistentBuiltinInstantiation`; the initially published `Instatiation`
spelling was corrected.

### JavaScript and accessibility additions (1.8.0)

The nursery gains `useDateNow`, `useErrorMessage`, `useThrowOnlyError`,
`useImportExtensions`, `useNumberToFixedDigitsArgument`, `useThrowNewError`,
`useTopLevelRegex`, `noYodaExpression`, `noUnusedFunctionParameters`,
`useSemanticElements`, `noSubstr`, `useConsistentCurlyBraces`,
`useValidAutocomplete`, `noShorthandPropertyOverrides`, `useDeprecatedReason`,
and `noExportedImports`.

`useImportExtensions` adds `suggestedExtensions`. `useSortedClasses` orders
known and dynamic Tailwind variants and puts arbitrary variants after known
ones, but does not support screen variants such as `sm:`, `max-md:`, or
`min-lg:`.

### CSS nursery additions (1.8.0)

CSS gains `noCssEmptyBlock`, `noDuplicateAtImportRules`, `noDuplicateFontNames`,
`noDuplicateSelectorsKeyframeBlock`, `noImportantInKeyframe`,
`noInvalidPositionAtImportRule`, `noUnknownFunction`,
`noUnknownMediaFeatureName`, `noUnknownProperty`, `noUnknownPseudoElement`,
`noUnknownPseudoClass`, `noUnknownUnit`, `noUnmatchableAnbSelector`, and
`useGenericFontNames`.

### Nursery additions (1.9-guide)

`noCommonJs`, `noDuplicateCustomProperties`, `noDynamicNamespaceImportAccess`,
`noEnum`, `noIrregularWhitespace`, `noRestrictedTypes`, `noSecrets`,
`noUselessEscapeInRegex`, `noValueAtRule`,
`useConsistentMemberAccessibility`, and `useTrimStartEnd` enter the nursery.

### Additional 1.9 rules (1.9.0)

The series adds `useAriaPropsSupportedByRole`, `useStrictMode`, `noProcessEnv`,
`noMissingVarFunction`, `useComponentExportOnlyModules`,
`noDescendingSpecificity`, `noNestedTernary`, `noTemplateCurlyInString`, and
`noOctalEscape`; then `useGuardForIn`, `noDocumentCookie`,
`noDocumentImportInPage`, `noDuplicateProperties`, `noHeadElement`,
`noHeadImportInDocument`, `noImgElement`, `noUnknownTypeSelector`, `useAtIndex`,
`noUselessStringRaw`, `useCollapsedIf`, `useGoogleFontDisplay`, and
`useExportsLast`.

### General additions (2.1.0)

The linter adds `noAlert`, `noImplicitCoercion`, `noMagicNumbers`,
`noUnassignedVariables`, `useReadonlyClassProperties`, and
`useUnifiedTypeSignature`.

### HTML accessibility additions (2.4-guide)

HTML, Vue, Svelte, and Astro gain `noAutofocus`, `noPositiveTabindex`,
`useAltText`, `useAnchorContent`, `useMediaCaption`, `useHtmlLang`,
`useValidLang`, `useValidAriaRole`, `useAriaPropsForRole`, `useButtonType`,
`noAccessKey`, `noDistractingElements`, `noSvgWithoutTitle`, `noRedundantAlt`,
and `useIframeTitle`.

### Playwright nursery additions (2.4.0)

The nursery adds `noConditionalExpect`, `useExpect`,
`usePlaywrightValidDescribeCallback`, `noPlaywrightElementHandle`,
`noPlaywrightEval`, `noPlaywrightForceOption`, `noPlaywrightMissingAwait`,
`noPlaywrightNetworkidle`, `noPlaywrightPagePause`,
`noPlaywrightUselessAwait`, `noPlaywrightWaitForNavigation`,
`noPlaywrightWaitForSelector`, and `noPlaywrightWaitForTimeout`.

### JavaScript nursery additions (2.4.0)

New rules are `noImpliedEval` for string timer arguments,
`noUnsafePlusOperands` for unsafe `+` and `+=` operand types,
`useImportsFirst`, `useNullishCoalescing`, `useNamedCaptureGroup`,
`useUnicodeRegex`, and `useArraySome`. `useArraySome` recognizes existence
checks built from `find`, `findLast`, and ES2025 iterator helpers.

### Framework, package, database, CSS, and JSON additions (2.4.0)

`noInlineStyles` covers HTML style attributes, JSX style props, and
`React.createElement`. `useVueScopedStyles` requires Vue SFC styles to use
`scoped` or `module`; `noVueRefAsOperand` catches refs used without `.value`.

`noUntrustedLicenses` can allow or deny identifiers, require OSI approval or
FSF-free status, and gives deny precedence. `noDrizzleUpdateWithoutWhere` and
`noDrizzleDeleteWithoutWhere` prevent whole-table updates or deletes.

CSS adds `noDuplicateSelectors` within an at-rule context and `useBaseline` for
properties, values, at-rules, media conditions, functions, and pseudo-selectors
outside a configured Baseline tier. JSON adds `noTopLevelLiterals` and
`noEmptyObjectKeys`.

## Promotions, removals, and renames

### Promotions (1.7-guide)

Stable groups gain `complexity/noExcessiveNestedTestSuites`,
`complexity/noUselessTernary`, `correctness/useJsxKeyInIterable`,
`performance/noBarrelFile`, `performance/noReExportAll`,
`style/noNamespaceImport`, `style/useNodeAssertStrict`,
`suspicious/noDuplicateTestHooks`, `suspicious/noExportsInTest`,
`suspicious/noFocusedTests`, `suspicious/noSkippedTests`, and
`suspicious/noSuspiciousSemicolonInJsx`.

### Promotions (1.8.0)

Stable groups gain `useImportRestrictions`, `noNodejsModules`,
`useArrayLiterals`, `noConstantMathMinMaxClamp`, and `noFlatMapIdentity`.

### Promotions and deprecated paths (1.9-guide)

Stable groups gain `noLabelWithoutControl`, `useFocusableInteractive`,
`useSemanticElements`, `noUselessStringConcat`,
`noUselessUndefinedInitialization`, `useDateNow`, `noUndeclaredDependencies`,
`noInvalidBuiltinInstantiation`, `noUnusedFunctionParameters`,
`useImportExtensions`, `useTopLevelRegex`, `noDoneCallback`,
`noYodaExpression`, `useConsistentBuiltinInstantiation`,
`useDefaultSwitchClause`, `useExplicitLengthCheck`, `useThrowNewError`,
`useThrowOnlyError`, `noConsole`, `noEvolvingTypes`, `noMisplacedAssertion`,
`noReactSpecificProps`, `useErrorMessage`, and
`useNumberToFixedDigitsArgument`.

Replace deprecated `correctness/noInvalidNewBuiltin`,
`style/useSingleCaseStatement`, and `suspicious/noConsoleLog` with
`correctness/noInvalidBuiltinInstantiation`, `correctness/noSwitchDeclarations`,
and `suspicious/noConsole` respectively.

### Promotions and removal (2.3.0)

Stable groups gain `suspicious/noNonNullAssertedOptionalChain`,
`style/useReactFunctionComponents`, `correctness/useImageSize`,
`style/useConsistentTypeDefinitions`, `correctness/useQwikClasslist`, and
`security/noSecrets`.

The nursery rule `useAnchorHref` is removed because `useValidAnchor` covers its
use case.

### Promotions (2.4-guide)

Correctness gains `noUnresolvedImports`, `noVueReservedProps`,
`noVueReservedKeys`, `noVueDataObjectDeclaration`,
`noNextAsyncClientComponent`, `noVueDuplicateKeys`,
`noVueSetupPropsReactivityLoss`, `useQwikMethodUsage`, and
`useQwikValidLexicalScope`.

Suspicious gains `noImportCycles`, `noDeprecatedImports`,
`noReactForwardRef`, `noUnusedExpressions`, `noEmptySource`,
`useDeprecatedDate`, and `noDuplicateDependencies`. Complexity gains
`noUselessUndefined`, `useMaxParams`, and `noUselessCatchBinding`. Style gains
`useConsistentArrowReturn` and `noJsxLiterals`.

### Large stable promotion (2.5-guide)

Seventy-three nursery rules move to stable groups. Promotion renames
`noFloatingClasses` to `noUnusedInstantiation`, `noMultiStr` to
`noMultilineString`, `useFind` to `useArrayFind`, and `useSpread` to
`useSpreadOverApply`.

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
- A11y: `noAmbiguousAnchorText`.

## Profiling

`biome lint --profile-rules` and `biome check --profile-rules` report total,
average, minimum, maximum, and invocation count for lint rules, assist actions,
and GritQL plugins; CST-query time is excluded (2.4-guide). Each plugin is
reported separately as `plugin/<pluginName>` as of 2.5.0.
