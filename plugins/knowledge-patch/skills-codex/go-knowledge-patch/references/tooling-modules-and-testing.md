# Tooling, Modules, and Testing

## Modules, workspaces, and dependency metadata

### Module checksums in `go list` (`1.23.0`)

`go list -m -json` reports `Sum` and `GoModSum`, matching the checksum fields
from `go mod download -json`.

### Operating on module tools as a set (`1.24.0`)

The `tool` meta-pattern covers every executable dependency named by a `tool`
directive in the current module. `go get tool` upgrades them together,
`go install tool` installs them into `GOBIN`, and
`go get -tool package@version` adds both the tool directive and required module
dependency.

### VCS-derived main module versions (`1.24.0`)

`go build` derives `runtime/debug.BuildInfo.Main.Version` from a VCS tag or
commit and appends `+dirty` for uncommitted changes. `-buildvcs=false` omits
this VCS information.

### Private-module authentication and toolchain tracing (`1.24.0`)

`GOAUTH` configures authentication for private module fetches.
`GODEBUG=toolchaintrace=1` traces `go` command toolchain selection.

### Module and workspace package selection (`1.25.0`)

A `go.mod` `ignore` directive excludes named directories and descendants from
package-pattern matching such as `all` and `./...`, but not from module zip
files. The `work` pattern selects every package in the work module or all
workspace modules. Updating a `go` line no longer adds a `toolchain` line for
the command's current version.

```go.mod
ignore ./generated
```

### Module roots in repository subdirectories (`1.25.0`)

A vanity import maps a module root to a repository subdirectory by placing that
subdirectory in a fourth `go-import` metadata field:
`root-path vcs repo-url subdir`.

### Conservative `go mod init` versions (`1.26.0`)

Under a stable 1.N toolchain, `go mod init` writes `go 1.(N-1).0`; a 1.N
prerelease writes `go 1.(N-2).0`. Thus the stable 1.26 toolchain defaults to
`go 1.25.0`, while its release candidates default to `go 1.24.0`. Run
`go get go@version` afterward to select another language version.

### Canonical `go mod tidy` require blocks (`1.27.0`)

For modules declaring Go 1.27 or later, `go mod tidy` consolidates duplicate
`require` blocks into at most one direct and one indirect block. Dependency
comments remain; a comment spanning both kinds attaches to the direct block.

## Command output, caches, and documentation

### Relocating the Go command (`1.23.0`)

`GOROOT_FINAL` no longer affects the installed toolchain. Distributions that
place `go` outside `$GOROOT/bin/go` must install a symlink instead of relocating
or copying the binary.

### Structured build events (`1.24.0`)

`go build -json` and `go install -json` emit structured build output and
failures. `go test -json` interleaves build and test records using distinct
`Action` values. `GODEBUG=gotestjsonbuildtext=1` restores textual build output
for an older integration.

### External build-cache programs (`1.24.0`)

`GOCACHEPROG` may name a child process implementing the `go` command's binary
and test cache through a JSON protocol; the facility is no longer experimental.

### Documentation and profiling tool changes (`1.26.0`)

`cmd/doc` and `go tool doc` are removed; use the flag-compatible `go doc`.
The `pprof -http` UI opens on the flame graph. The former graph view is under
`View -> Graph` or `/ui/graph`.

### Tool response files (`1.27.0`)

`compile`, `link`, `asm`, `cgo`, `cover`, and `pack` accept `@file` response
files. Arguments are whitespace-separated with single or double quotes,
escapes, and backslash-newline continuation in a GCC-compatible format.

```sh
go tool compile @compile.args
```

### Typed `go test -json` output (`1.27.0`)

Test output events may include an optional `OutputType` field with values such
as `error`, `error-continue`, or `frame`. Consumers must tolerate this field and
future additions.

### Versioned and example-aware `go doc` (`1.27.0`)

`go doc` accepts `package@version`; `-ex` lists executable examples. Asking for
a named example prints its source and comments.

```sh
go doc example.com/pkg@v1.2.3
go doc -ex bytes
```

## Vet and source modernization

### New vet failures (`1.24.0`)

The `tests` analyzer, also run by `go test`, finds malformed test, fuzz,
benchmark, and example declarations. For language version 1.24 or later, vet
diagnoses non-constant `fmt.Printf(s)` calls without formatting arguments.
Build constraints may name only a major Go release, so `go1.23.1` is invalid.

### New vet diagnostics (`1.25.0`)

The `waitgroup` analyzer reports misplaced `sync.WaitGroup.Add` calls. The
`hostport` analyzer reports `fmt.Sprintf("%s:%d", host, port)` addresses that
fail for IPv6 and recommends `net.JoinHostPort`.

### Modernizing code with `go fix` (`1.26.0`)

The analysis-based `go fix` applies behavior-preserving modernizers. A function
annotated `//go:fix inline` can drive source-level inlining for automated API
migrations. Obsolete historical fixers are removed.

### Default `stdversion` checks (`1.27.0`)

`go test` runs the `stdversion` vet analyzer by default and reports
standard-library symbols newer than the version selected by module and file
build tags.

### `go fix` analyzer changes (`1.27.0`)

`go fix` adds `atomictypes`, `embedlit`, `slicesbackward`, and `unsafefuncs`.
`fmtappendf` is removed, and `waitgroup` is renamed to `waitgroupgo`.

### Declarations of removed `GODEBUG` settings (`1.27.0`)

A `go.mod` `godebug` entry or `//go:debug` comment may still name a removed
setting only with its final default value. Naming its obsolete value fails the
build rather than restoring removed behavior.

## Concurrency tests and test lifecycle

### Experimental deterministic concurrency tests (`1.24-guide`)

The initial `testing/synctest` API requires `GOEXPERIMENT=synctest` and is not
covered by compatibility guarantees. `Run` creates an isolated bubble for the
callback and descendants; `Wait` returns when the other goroutines are durably
blocked and supplies synchronization understood by the race detector.

### Bubble time and blocking rules (`1.24-guide`)

Inside a synctest bubble, `time` uses a fake clock that advances only when every
goroutine is durably blocked. Durable operations include nil or same-bubble
channels, selects containing only durable cases, `time.Sleep`,
`sync.Cond.Wait`, and `sync.WaitGroup.Wait`; mutex acquisition and external I/O
do not qualify. A channel created inside a bubble panics if used outside it.

Use `net.Pipe` or another in-memory substitute for network tests. The initial
`Run` API waits for all bubble goroutines and panics on an unresolved deadlock,
so every background goroutine must exit.

### Test-scoped contexts (`1.24.0`)

`T.Context` and `B.Context` return a context canceled after the test or
benchmark finishes but before cleanup functions run.

### Stabilized `testing/synctest` (`1.25.0`)

The stable API uses `synctest.Test` and `synctest.Wait` without an experiment.
The older `Run` remains only under `GOEXPERIMENT=synctest` and is scheduled for
removal in 1.26.

### Test attributes, output, and allocation checks (`1.25.0`)

`T.Attr`, `B.Attr`, and `F.Attr` add key/value attributes to logs and JSON
events. Their `Output` methods return an indented log writer without file and
line prefixes. `testing.AllocsPerRun` panics while parallel tests are running
instead of producing a flaky measurement.

### Persistent test artifacts (`1.26.0`)

`T.ArtifactDir`, `B.ArtifactDir`, and `F.ArtifactDir` return an output
directory. With `go test -artifacts`, it persists under `-outputdir` or the
current directory and is logged on first use; otherwise it is temporary and
removed after the test.

## Supported release lines

### Support window and maintenance releases (`rolling-2026-08-19`)

The 1.27.0 release leaves 1.27 and 1.26 as the supported lines under the
two-release policy; 1.25 is no longer supported. The older supported line is at
1.26.7, issued on 2026-08-19 with `net/http` fixes. The same package-level fix
appeared in 1.25.14 for users not yet migrated, but those users should move to
1.26 or 1.27.
