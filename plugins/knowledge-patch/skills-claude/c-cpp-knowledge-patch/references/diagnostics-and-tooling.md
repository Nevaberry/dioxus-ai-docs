# Diagnostics and tooling

Use this reference when compiler upgrades affect warnings, diagnostic parsers,
format configuration, Clang embedding, libclang/Python clients, AST matchers,
GCC plugins, or Static Analyzer configurations.

## Diagnostic output and CI consumers

### GCC machine-readable output

GCC 15 deprecates `-fdiagnostics-format=json`; use SARIF for machine-readable
diagnostics (`gcc-15.1`). It can emit multiple formats from one compilation
with `-fdiagnostics-add-output=`, while `-fdiagnostics-set-output=` provides
more detailed control.

GCC 16 removes the `json` value entirely (`gcc-16.1`). Migrate parsers before
the compiler upgrade and validate path, location, nesting, and fix-it handling
against SARIF.

### Hierarchical C++ diagnostics

GCC 16 presents nested explanations for C++ diagnostics (`gcc-16.1`). Use
`-fno-diagnostics-show-nesting` or `-fdiagnostics-plain-output` when a tool or
human workflow requires the former flat form.

### Clang suppression mappings

Clang 20 accepts `-warning-suppression-mappings` for per-file Static Analyzer
suppression (`clang-20.1`). Clang 22 changes overlapping mapping precedence:
the last matching entry wins rather than the longest match (`clang-22.1`).
Reorder existing files so the intended rule is last and add an overlap test.

### GCC installation discovery

Clang 22 warns with `-Wgcc-install-dir-libstdcxx` when automatic discovery
selects the highest-version GCC installation even though it lacks libstdc++
headers and another complete installation exists (`clang-22.1`). Make the
installations consistent, select one with `--gcc-install-dir`, or suppress the
warning only when the incomplete selection is intentional.

## Warning-policy changes

### Clang 20 warning groups

Clang 20 adds or changes these controls (`clang-20.1`):

- `-Warray-compare` diagnoses array comparisons before C++20;
  `-Warray-compare-cxx26` covers C++26 onward and is an error by default.
- `-Wnontrivial-memcall` checks non-trivially-copyable destinations passed to
  memory functions and is implied by `-Wnontrivial-memaccess`.
- `-Winvalid-gnu-asm-cast` is enabled and is an error by default.
- `-fheinous-gnu-extensions` is deprecated as an alias for demoting that GNU
  assembly diagnostic.
- `-Wdangling-assignment-gsl` is enabled by default.

### GCC 15 source-policy warnings

`-Wheader-guard` is new and enabled by `-Wall` in GCC 15 (`gcc-15.1`).
`-Wtrailing-whitespace=` and `-Wleading-whitespace=` provide whitespace-policy
checks. Pin them explicitly if exact CI behavior matters.

GCC 15 also accepts C++11 attribute syntax in C++98 mode, supports `flag_enum`
to suppress inappropriate switch warnings, and adds
`-Wdefaulted-function-deleted` for explicitly defaulted functions that become
deleted (`gcc-15.1`).

### Clang 21 warning and thread-safety coverage

Clang 21 adds `-Wunique-object-duplication`, `-Wshift-bool`, and
`-Wunnecessary-virtual-specifier`, the latter under `-Wextra`
(`clang-21.1`). Unsafe libc calls move to
`-Wunsafe-buffer-usage-in-libc-call`.

Thread-safety analysis adds opt-in `-Wthread-safety-pointer` and reentrant
capabilities. The pointer analysis performs no alias analysis, so interpret
results within that limitation.

### Clang 22 group membership and new warnings

Pedantic function-effect redeclaration checks move to
`-Wfunction-effect-redeclarations`, and
`-Wperf-constraint-implies-noexcept` leaves `-Wall` (`clang-22.1`). New groups
include `-Walloc-size`, `-Wenum-compare-typo`, and `-Wshadow-header`.
`ACQUIRED_BEFORE` and `ACQUIRED_AFTER` no longer require
`-Wthread-safety-beta`. `-Wformat-nonliteral` can diagnose wrappers missing a
`format` or `format_matches` annotation.

### GCC 16 unused-but-set levels

`-Wunused-but-set-variable` and `-Wunused-but-set-parameter`, including through
`-Wall` or `-Wextra`, default to level 3 in GCC 16
(`gcc-16.1-porting`). Level 2 stops treating increment/decrement as use; level
3 also stops treating compound assignment as use when its old value is absent
from the right-hand side. Level 1 approximates older behavior for staged
migration:

```text
-Wunused-but-set-variable=1 -Wunused-but-set-parameter=1
```

## clang-format

### Configuration added in Clang 20

Clang 20 adds `BreakBinaryOperations`, `TemplateNames`,
`RemoveEmptyLinesInUnwrappedLines`, `KeepFormFeed`,
`AllowShortNamespacesOnASingleLine`, `VariableTemplates`,
`WrapNamespaceBodyWithEmptyLines`, `IndentExportBlock`, and
`PenaltyBreakBeforeMemberAccess` (`clang-20.1`). GNU style enables
`KeepFormFeed`.

`AlignConsecutiveDeclarations` gains `AlignFunctionDeclarations`.
`ReflowComments` gains `IndentOnly`, and its boolean values become
`Never`/`Always`. Ignore files support Bash globstar. C is formatted as a
distinct language, and a header can force a language with a first-line comment
such as `// clang-format Language: ObjC`.

### Configuration added in Clang 21

Clang 21 adds `BreakBeforeTemplateCloser`, `BinPackLongBracedList`,
`EnumTrailingComma`, `OneLineFormatOffRegex`, `SpaceAfterOperatorKeyword`, and
`MacrosSkippedByRemoveParentheses` (`clang-21.1`).

### Configuration changed in Clang 22

`AlignAfterOpenBracket` becomes boolean in Clang 22; `AlwaysBreak` and
`BlockIndent` are deprecated (`clang-22.1`). New controls include
`SpaceInEmptyBraces`, `NumericLiteralCase`, `IndentPPDirectives: Leave`, the
`BreakAfterOpenBracket*` and `BreakBeforeCloseBracket*` families, and
`AlignPPAndNotPP`.

Integer-separator `*MinDigits` keys are renamed to `*MinDigitsInsert`, with new
`*MaxDigitsSeparator` keys. Update configuration schema and reformat a
representative corpus before accepting changes.

## Clang libraries and embedding

### Link dependencies in Clang 22

Options code moves from `clangDriver` to the new `clangOptions` library
(`clang-22.1`). Downstream tools using it may need both. `clangFrontend` also
stops depending transitively on `clangDriver`; consumers of driver APIs must
link `clangDriver` explicitly.

### libclang layout and pretty-print APIs

Clang 20 adds `clang_isBeforeInTranslationUnit`, policy-controlled
`clang_getTypePrettyPrinted`, `clang_visitCXXBaseClasses`, and
`clang_getOffsetOfBase` (`clang-20.1`). Python bindings expose pretty printing,
base iteration, virtual-base queries, and base offsets.

Affected Python string-returning interfaces return `""` rather than `None`
when absent. Accessing `CompletionChunk` or `CompletionString` properties
statically is an error.

### libclang method and assembly APIs

Clang 21 adds inline-assembly queries, `clang_visitCXXMethods`, and
`clang_getFullyQualifiedName`; duplicate binary-opcode APIs are deprecated
(`clang-21.1`). Python bindings add hashable cursors, attribute and template
queries, method visits, fully qualified names, and `File` equality.

`Cursor.from_location` now returns `None` rather than a null cursor, and most
cursor methods reject null cursors. Update sentinel tests before invoking
methods.

### Clang 22 AST interfaces

In Clang 22, `VarTemplateSpecializationDecl::getTemplateArgsAsWritten()` returns
null for implicit instantiations (`clang-22.1`). Anonymous-record members are
injected as invalid `IndirectFieldDecl` objects even on name conflicts, while
abbreviated function templates and generic lambdas gain valid begin locations.

The `elaboratedType` and `dependentTemplateSpecializationType` matchers are
removed. Added facilities include `MatchFinderOptions::IgnoreSystemHeaders`,
`hasConditionVariableStatement` for `for`, `while`, and `switch`, and the
`arrayTypeLoc` matcher.

### Clang 22 Python failure and null handling

`Token.cursor` returns `None` rather than a null cursor, `TypeKind.ELABORATED`
is no longer produced, `AccessSpecifier.NONE` is removed, and
`TranslationUnit.reparse()` raises on errors (`clang-22.1`).
`LIBCLANG_LIBRARY_PATH` and `LIBCLANG_LIBRARY_FILE` select libclang. Bindings
also expose cursor language, inline-function queries, and formerly missing
cursor, type, and exception kinds.

## Static Analyzer

### Clang 20 effects, timeouts, and checker migration

The analyzer verifies `nonblocking` and `nonallocating` function effects in
Clang 20 (`clang-20.1`). Its Z3 cross-check timeout returns from 300 ms to 15
seconds, while rlimit and equivalence-class timeout defaults become disabled.

Several alpha checkers graduate or move:

- `alpha.unix.Chroot` becomes `unix.Chroot`;
- `alpha.core.PointerSub` becomes `security.PointerSub`;
- taint checkers move under `optin.taint.*`; and
- the two nondeterministic-pointer checkers become clang-tidy's
  `bugprone-nondeterministic-pointer-iteration-order`.

### Clang 21 assumptions and array bounds

Clang 21 understands `[[clang::assume]]` and adds
`core.FixedAddressDereference` (`clang-21.1`).
`alpha.security.ArrayBoundV2` graduates to `security.ArrayBound`, replacing the
old alpha checker. The long-deprecated
`optin.cplusplus.VirtualCall:PureOnly` option is removed.

### Clang 22 checker and configuration changes

Clang 22 adds `core.NullPointerArithm` and `alpha.core.StoreToImmutable`
(`clang-22.1`). All `valist.*` functionality moves to `security.VAList`, and
`alpha.core.CastSize` is removed. `[[clang::suppress]]` now works in primary
templates. Analyzer model paths and taint configurations honor virtual-file-
system overlays.

## GCC plugin diagnostics API migration

GCC 16 moves diagnostic internals below `gcc/diagnostics/` and into the
`diagnostics::` namespace (`gcc-16.1-porting`). Plugins using internal context,
path, sink, buffering, SARIF, printing, or edit APIs require new headers and
source changes. Important replacements include:

| Former API | Replacement |
| --- | --- |
| `diagnostic_context` | `diagnostics::context` |
| `diagnostic_output_format` | `diagnostics::sink` |
| `diagnostic_path` | `diagnostics::paths::path` |
| `edit_context` | `diagnostics::changes::change_set` |
| `sarif_output_format` | `diagnostics::sarif_sink` |
