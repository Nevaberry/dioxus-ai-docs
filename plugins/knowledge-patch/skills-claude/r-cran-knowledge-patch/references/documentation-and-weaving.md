# Documentation and Weaving

The documentation changes are attributed to `r-4.6.0` and `r-4.6.1`.

## Rd links

- Cross-package S4 class links use `\linkS4class[pkg]{Class}`. A package
  using this syntax must depend on R 4.6.0 or later.
- `\linkS4methods{}` links to S4 method documentation.
- `\manual{name}{node}` links to a section of an R manual.

## Equations, citations, and references

- Plain-text and legacy-HTML conversion of simple Rd `\eqn{}` markup
  recognizes `\geq`, `\leq`, `\neq`, and `\ne`, in addition to `\ge` and
  `\le` (`r-4.6.1`).
- Rd citations and reference lists can be generated from `bibentry` data or
  from R/BibTeX bibliographic databases.
- `tools::deparseLatex(math = ...)` can turn `$...$` fields into Rd equation
  markup.

## Installed documentation and LaTeX compatibility

- Package `README.md` files are installed and shown in HTML help.
- The bundled `jss.cls` works with `hyperref` 7.01q dated 2026-04-24,
  avoiding that version-specific document-build incompatibility
  (`r-4.6.1`).

## Sweave weaving and tangling

- `RweaveLatex` can take logical or numeric chunk options from objects
  computed in earlier chunks.
- The `ignore.on.weave`, `ignore.on.tangle`, `weave`, `tangle`, and `ignore`
  controls separate weaving from tangling.
- `Rtangle` accepts `chunk.sep`.
- For split files, `Rtangle` accepts `extension`.
- `SweaveGetSourceName()` returns the command-line source name.
