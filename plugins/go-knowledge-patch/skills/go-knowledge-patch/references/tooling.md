# Tooling

## `go fix` Modernizers (1.26)

`go fix` has been completely rewritten. It now runs dozens of modernizers that update code to current Go idioms and APIs. Built on the `go/analysis` framework (same infrastructure as `go vet`).

### Usage

```bash
go fix ./...
```

### `//go:fix inline` Directive

Supports custom API migration rules via the `//go:fix inline` directive, allowing library authors to mark deprecated functions for automatic replacement:

```go
//go:fix inline
func OldAPI(x int) int { return NewAPI(x, defaultOpt) }
```

When users run `go fix`, calls to `OldAPI(x)` are automatically rewritten to `NewAPI(x, defaultOpt)`.
