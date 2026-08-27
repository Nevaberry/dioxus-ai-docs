# Libraries and Tooling

Use this reference for standard-library upgrades, modules, machine diagnostics, formatter configuration, compiler embedding, AST tooling, bindings, and plugins.

## libstdc++ source migration

### Include owning headers directly

GCC 15 (`gcc-15.1-porting`) exposes fewer transitive headers. Include `<stdint.h>` for global fixed-width integer typedefs, `<cstdint>` for their `std::` forms, and `<ostream>` for stream declarations, `std::endl`, and `std::flush`.

Remove compatibility headers that now warn: replace `<cstdbool>` and `<cstdalign>` with nothing, `<ccomplex>` with `<complex>`, and `<ctgmath>` with `<cmath>`, `<complex>`, or both.

### Constrain iterator adaptors accurately

The GCC 15.1 (`gcc-15.1-porting`) `std::vector` range constructor recognizes C++20 iterator concepts and may select a stronger optimized path. An adaptor that exposes invalid operations unconditionally can fail during instantiation. Constrain each operation to the wrapped iterator's real capability, using equivalent SFINAE in older modes:

```cpp
iterator_adaptor& operator--()
  requires std::bidirectional_iterator<Iter>
{
  --iter;
  return *this;
}
```

### Debug assertions

GCC 15 (`gcc-15.1`) enables libstdc++ debug assertions by default in unoptimized builds. Define `_GLIBCXX_NO_ASSERTIONS` only when the build intentionally needs the former unchecked behavior.

## Standard-library feature additions

### GCC 15 library facilities

GCC 15 (`gcc-15.1`) adds experimental C++26 facilities including `views::concat`, `views::to_input`, `views::cache_latest`, constexpr sorting and raw-memory algorithms, `<stdbit.h>`, `<stdckdint.h>`, `std::is_virtual_base_of`, member `visit`, and compile-time type checking for `std::format` arguments.

Its C++23 library adds the `std` and `std.compat` modules, flat associative containers, range constructors and modifiers, and range and tuple formatting.

### GCC 16 library facilities

GCC 16 (`gcc-16.1`) adds C++23 `std::mdspan`, starts/ends-with range algorithms, shift algorithms, and `allocate_at_least`.

C++26 additions include `std::simd`, `std::inplace_vector`, `std::optional<T&>`, `std::copyable_function`, `std::function_ref`, `std::indirect`, `std::polymorphic`, `std::owner_equal`, `<debugging>`, string-view overloads, padded `mdspan` layouts, `std::philox_engine`, and `std::atomic_ref::address()`.

## Modules and precompiled artifacts

Clang 20 (`clang-20.1`) makes `-fmodules-reduced-bmi` the non-experimental spelling for reduced BMIs.

Clang 22 (`clang-22.1`) enables Reduced BMI mode by default for C++20 modules. Two-phase module builds must handle the reduced artifact, and projects must not depend on implementation details discarded from it.

GCC 16 (`gcc-16.1`) adds `--compile-std-module` for experimental C++20 modules. It builds the `<bits/stdc++.h>` header unit and the `std` and `std.compat` modules before explicit inputs; after that header unit exists, eligible standard-header includes can become imports.

## Machine-readable diagnostics

GCC 15 (`gcc-15.1`) deprecates the `json` value of `-fdiagnostics-format=` in favor of SARIF. `-fdiagnostics-add-output=` can emit several formats from one compilation, while `-fdiagnostics-set-output=` provides more explicit output control.

GCC 16 (`gcc-16.1`) removes the JSON value entirely. Diagnostic consumers must use SARIF.

## Compiler discovery and embedding

### GCC installation discovery

Clang 22 (`clang-22.1`) warns with `-Wgcc-install-dir-libstdcxx` when automatic discovery selects the highest GCC installation but it lacks libstdc++ headers while another complete installation exists. Install or remove headers consistently, choose a tree with `--gcc-install-dir`, or deliberately suppress with `-Wno-gcc-install-dir-libstdcxx`.

### Clang library dependencies

Clang 22 (`clang-22.1`) moves option-related code from `clangDriver` into the new `clangOptions` library. Downstream tools may need both. `clangFrontend` no longer depends transitively on `clangDriver`, so consumers that use driver APIs must link it explicitly.

## clang-format configuration

### Clang 20 schema

Clang 20 (`clang-20.1`) adds `BreakBinaryOperations`, `TemplateNames`, `RemoveEmptyLinesInUnwrappedLines`, `KeepFormFeed`, `AllowShortNamespacesOnASingleLine`, `VariableTemplates`, `WrapNamespaceBodyWithEmptyLines`, `IndentExportBlock`, and `PenaltyBreakBeforeMemberAccess`. GNU style enables `KeepFormFeed`.

`AlignConsecutiveDeclarations` gains `AlignFunctionDeclarations`. `ReflowComments` gains `IndentOnly` and renames boolean values to `Never`/`Always`. Ignore files understand bash globstar. C becomes its own formatting language, and a top-of-file comment such as `// clang-format Language: ObjC` can force a header's language.

### Clang 21 schema

Clang 21 (`clang-21.1`) adds `BreakBeforeTemplateCloser`, `BinPackLongBracedList`, `EnumTrailingComma`, `OneLineFormatOffRegex`, `SpaceAfterOperatorKeyword`, and `MacrosSkippedByRemoveParentheses`.

### Clang 22 schema

Clang 22 (`clang-22.1`) makes `AlignAfterOpenBracket` boolean; `AlwaysBreak` and `BlockIndent` are deprecated. It adds `SpaceInEmptyBraces`, `NumericLiteralCase`, `IndentPPDirectives: Leave`, `BreakAfterOpenBracket*`, `BreakBeforeCloseBracket*`, and `AlignPPAndNotPP`.

Integer-separator `*MinDigits` keys become `*MinDigitsInsert`, and new `*MaxDigitsSeparator` keys set upper separator grouping limits.

## libclang and Python bindings

### Layout and pretty-printing APIs

Clang 20 (`clang-20.1`) adds `clang_isBeforeInTranslationUnit`, policy-controlled `clang_getTypePrettyPrinted`, `clang_visitCXXBaseClasses`, and `clang_getOffsetOfBase`. Python bindings expose pretty printing, base iteration, virtual-base queries, and base offsets.

Affected Python string-returning interfaces return `""` rather than `None` when absent. Accessing `CompletionChunk` or `CompletionString` properties statically is an error.

### Method and assembly queries

Clang 21 (`clang-21.1`) adds libclang inline-assembly queries, `clang_visitCXXMethods`, and `clang_getFullyQualifiedName`; duplicate binary-opcode APIs are deprecated.

Python's `Cursor.from_location` returns `None` rather than a null cursor, and most cursor methods reject null cursors. Bindings add hashable cursors, attribute/template queries, method visits, fully qualified names, and `File` equality.

### Failure and null handling

Clang 22 (`clang-22.1`) makes `Token.cursor` return `None` rather than a null cursor, stops producing `TypeKind.ELABORATED`, removes `AccessSpecifier.NONE`, and makes `TranslationUnit.reparse()` raise on errors.

`LIBCLANG_LIBRARY_PATH` and `LIBCLANG_LIBRARY_FILE` can select libclang. Bindings expose cursor language, inline-function queries, and previously missing cursor, type, and exception kinds.

## AST tooling interfaces

Clang 22 (`clang-22.1`) makes `VarTemplateSpecializationDecl::getTemplateArgsAsWritten()` return null for implicit instantiations. Anonymous-record members are injected as invalid `IndirectFieldDecl`s even on name conflicts, while abbreviated function templates and generic lambdas receive valid begin locations.

The `elaboratedType` and `dependentTemplateSpecializationType` matchers are removed. Additions include `MatchFinderOptions::IgnoreSystemHeaders`, `hasConditionVariableStatement` for `for`, `while`, and `switch`, and the `arrayTypeLoc` matcher.

## GCC plugin migration

GCC 16 (`gcc-16.1-porting`) moves diagnostic internals below `gcc/diagnostics/` and into the `diagnostics::` namespace. Plugins using context, path, sink, buffering, SARIF, printing, or edit internals need new headers and source changes. Major replacements include:

| Old API | New API |
| --- | --- |
| `diagnostic_context` | `diagnostics::context` |
| `diagnostic_output_format` | `diagnostics::sink` |
| `diagnostic_path` | `diagnostics::paths::path` |
| `edit_context` | `diagnostics::changes::change_set` |
| `sarif_output_format` | `diagnostics::sarif_sink` |
