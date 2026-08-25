# Tooling, Modules, and Testing

## Module and dependency operations

### Module metadata and checksums (1.23.0)

`go list -m -json` emits `Sum` and `GoModSum`, matching
`go mod download -json`.

### Tool dependencies and package selection (1.24.0, 1.25.0)

The `tool` meta-pattern denotes every executable dependency named by a `tool`
directive. `go get tool` upgrades the set, `go install tool` installs it into
`GOBIN`, and `go get -tool package@version` adds both the directive and the
required module dependency.

A `go.mod` `ignore` directive excludes named directories and descendants from
package patterns such as `all` and `./...`; it does not exclude those files
from module zips. The `work` pattern selects every package in the current work
module, or in all workspace modules. Updating a `go` line no longer adds a
`toolchain` line for the running command.

Vanity import metadata can map a module root to a repository subdirectory by
adding a fourth `subdir` field: `root-path vcs repo-url subdir`.

### Conservative initialization and canonical tidy output (1.26.0, 1.27.0)

Under a stable 1.N toolchain, `go mod init` writes `go 1.(N-1).0`; under a 1.N
prerelease it writes `go 1.(N-2).0`. A stable Go 1.26 command therefore starts
at `go 1.25.0`; select another version afterward with `go get go@version`.

For modules declaring Go 1.27 or later, `go mod tidy` consolidates duplicate
`require` blocks into at most one direct and one indirect block. It preserves
dependency comments; a comment spanning both classes attaches to the direct
block.

## Command output and integrations

### Relocating the command and private access (1.23.0, 1.24.0)

`GOROOT_FINAL` no longer relocates the installed `go` executable. A
distribution that does not place it at `$GOROOT/bin/go` must install a symlink,
not copy or relocate the binary.

`GOAUTH` configures private-module fetch authentication.
`GODEBUG=toolchaintrace=1` traces toolchain selection.

### Structured build and test records (1.24.0, 1.27.0)

`go build -json` and `go install -json` emit structured build output and
failures. `go test -json` interleaves build and test records using additional
`Action` values; `GODEBUG=gotestjsonbuildtext=1` temporarily restores textual
build output for older integrations.

Test output events may also include `"OutputType"` values such as `"error"`,
`"error-continue"`, or `"frame"`. Consumers must tolerate unknown optional
fields and evolving action values.

### Build information and external caches (1.24.0)

`runtime/debug.BuildInfo.Main.Version` is derived from a VCS tag or commit;
dirty working trees append `+dirty`. `-buildvcs=false` omits VCS information.

`GOCACHEPROG` names a child process implementing the binary and test cache over
a JSON protocol; it is no longer experimental.

### Tool response files (1.27.0)

`compile`, `link`, `asm`, `cgo`, `cover`, and `pack` accept `@file` response
files. Arguments use GCC-compatible whitespace separation, single or double
quotes, escapes, and backslash-newline continuation:

```sh
go tool compile @compile.args
```

## Vet, fix, documentation, and profiling

### Vet diagnostics (1.24.0, 1.25.0, 1.27.0)

- The `tests` analyzer reports malformed test, fuzz, benchmark, and example
  declarations and also runs under `go test`.
- For language version 1.24 or later, vet reports non-constant `fmt.Printf(s)`
  with no formatting arguments.
- Version build tags may name only a major Go release; `go1.23.1` is invalid.
- The `waitgroup` analyzer reports misplaced `sync.WaitGroup.Add`; `hostport`
  reports address formatting that fails for IPv6 and recommends
  `net.JoinHostPort`.
- `go test` runs `stdversion` by default, detecting standard-library symbols
  newer than the selected module or file language version.

### Analysis-based `go fix` (1.26.0, 1.27.0)

`go fix` uses the analysis framework for behavior-preserving modernizers.
`//go:fix inline` marks a function whose source-level inlining can drive an API
migration; obsolete historical fixers are gone.

The newer analyzer set includes `atomictypes`, `embedlit`, `slicesbackward`,
and `unsafefuncs`; `fmtappendf` is removed and `waitgroup` is renamed to
`waitgroupgo`.

### Documentation and pprof (1.26.0, 1.27.0)

`cmd/doc` and `go tool doc` are removed; use `go doc`. It additionally accepts
`package@version`, while `-ex` lists executable examples and a named example
prints its source and comments.

```sh
go doc example.com/pkg@v1.2.3
go doc -ex bytes
```

`pprof -http` opens on the flame graph. The old graph remains at
`View -> Graph` or `/ui/graph`.

## Concurrency tests and lifecycle

### Synctest bubbles (1.24-guide, 1.25.0)

The experimental `testing/synctest.Run` API introduced behind
`GOEXPERIMENT=synctest` was replaced by stable `synctest.Test` and `Wait`.
Do not retain the old `Run` experiment dependency.

Within a bubble, `time` uses a fake clock and advances to the next event only
when every goroutine is durably blocked. Durable operations include nil or
same-bubble channel operations, selects with only durable cases, `time.Sleep`,
`sync.Cond.Wait`, and `sync.WaitGroup.Wait`; mutex acquisition and external I/O
are not durable.

Use in-memory substitutes such as `net.Pipe`. A channel created inside a bubble
panics if used outside it. The test waits for all bubble goroutines and panics
on unresolved deadlock, so every background goroutine must exit. `Wait` is
synchronization understood by the race detector.

### Contexts, structured logs, and allocation checks (1.24.0, 1.25.0)

`T.Context` and `B.Context` are canceled after the test or benchmark finishes
but before cleanup functions run.

`T.Attr`, `B.Attr`, and `F.Attr` attach key/value attributes to logs and JSON
events. Their `Output` methods return an indented writer without file and line
prefixes. `testing.AllocsPerRun` panics if parallel tests are running.

### Persistent artifacts (1.26.0)

`T.ArtifactDir`, `B.ArtifactDir`, and `F.ArtifactDir` return a diagnostic-output
directory. With `go test -artifacts`, it persists beneath `-outputdir` or the
current directory and is logged on first use. Otherwise it is temporary and
removed after the test.

### AddressSanitizer leak reports (1.25.0)

Programs built with `go build -asan` perform leak detection at exit. Use
`ASAN_OPTIONS=detect_leaks=0` at runtime only when those reports must be
disabled.

## Removed compatibility declarations

### Final-default-only `GODEBUG` entries (1.27.0)

A removed setting is accepted in a `go.mod` `godebug` entry or `//go:debug`
comment only when it declares the final default. Asking for the obsolete value
fails the build rather than restoring old behavior.

## Supported release lines

### Maintenance policy (rolling-2026-08-19)

Go supports the latest two release lines. After Go 1.27.0, those are 1.27 and
1.26; 1.25 is unsupported. The older supported line's maintenance release is
Go 1.26.7, issued with `net/http` fixes. Go 1.25.14 carries the same package fix
for migration laggards, who should move to 1.26 or 1.27.
