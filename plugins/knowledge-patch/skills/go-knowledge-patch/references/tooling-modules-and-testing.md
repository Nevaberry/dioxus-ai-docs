# Tooling, Modules, and Testing

Batch coverage: `1.23.0`, `1.24-guide`, `1.24.0`, `1.25.0`, `1.26.0`.

## Contents

- [Modules and dependencies](#modules-and-dependencies)
- [Build and command output](#build-and-command-output)
- [Analysis and modernization](#analysis-and-modernization)
- [Deterministic concurrency tests](#deterministic-concurrency-tests)
- [Test lifecycle and output](#test-lifecycle-and-output)
- [Profiling tools](#profiling-tools)

## Modules and dependencies

### Module checksums

`go list -m -json` includes `Sum` and `GoModSum`, matching the checksum fields from `go mod download -json`.

### Module tool dependencies

The `tool` meta-pattern denotes every executable dependency named by a `tool` directive in the current module:

```sh
go get tool
go install tool
```

The first command upgrades the tools as a set; the second installs them into `GOBIN`. Use `go get -tool package@version` to add both a tool directive and the required module dependency.

### Package-pattern selection

The `go.mod` `ignore` directive excludes a named directory and all descendants from package-pattern matching such as `all` and `./...`. It does not exclude those files from module zip archives.

```go.mod
ignore ./generated
```

The `work` pattern selects every package in the current work module, or in all workspace modules. Updating a `go` line no longer adds a `toolchain` line for the command's current version.

### Repository subdirectories in vanity imports

Map a module root to a repository subdirectory by adding a fourth field to `go-import` metadata:

```text
root-path vcs repo-url subdir
```

### Conservative `go mod init` versions

Under a stable 1.N toolchain, `go mod init` writes `go 1.(N-1).0`; under a 1.N prerelease it writes `go 1.(N-2).0`. Thus stable Go 1.26 defaults to `go 1.25.0`, while its release candidates default to `go 1.24.0`. Run `go get go@version` afterward to choose another language version.

### Private modules and toolchain selection

Set `GOAUTH` to configure authentication for private-module fetches. Set `GODEBUG=toolchaintrace=1` to trace the `go` command's toolchain-selection decisions.

## Build and command output

### Structured build events

`go build -json` and `go install -json` emit structured build output and failures. `go test -json` interleaves build records with test records using additional `Action` values. Integrations that still require textual build output can temporarily set `GODEBUG=gotestjsonbuildtext=1`.

### VCS-derived main-module versions

`go build` derives `runtime/debug.BuildInfo.Main.Version` from a VCS tag or commit and appends `+dirty` for uncommitted changes. Pass `-buildvcs=false` to omit VCS information.

### External build caches

`GOCACHEPROG` can name a child process implementing the `go` command's binary and test cache through a JSON protocol; this capability is no longer experiment-gated.

### AddressSanitizer leaks

Programs built with `go build -asan` perform leak detection at exit by default. Set `ASAN_OPTIONS=detect_leaks=0` when running the program to disable those reports.

### Documentation command removal

`cmd/doc` and `go tool doc` are removed. Use the flag-compatible `go doc` command.

## Analysis and modernization

### Vet diagnostics

The `tests` analyzer, also run by `go test`, reports malformed test, fuzz, benchmark, and example declarations. For code selecting language version 1.24 or later, vet reports non-constant `fmt.Printf(s)` calls with no formatting arguments. Version build constraints may name only a major Go release, so a tag such as `go1.23.1` is invalid.

The `waitgroup` analyzer reports misplaced `sync.WaitGroup.Add` calls. The `hostport` analyzer reports address construction such as `fmt.Sprintf("%s:%d", host, port)`, which breaks for IPv6, and recommends `net.JoinHostPort`.

### Analysis-based `go fix`

The rewritten `go fix` uses the Go analysis framework to apply many behavior-preserving modernizers. A function annotated with `//go:fix inline` can specify source-level inlining for automated API migrations. The historical fixers were removed.

### Source-analysis APIs

- `ast.PreorderStack` traverses syntax while exposing the enclosing-node stack.
- `token.FileSet.AddExistingFiles` assembles a file set from existing files.
- `types.Var.Kind` exposes variable classification.
- `types.LookupSelection` exposes selections.
- `ast.ParseDirective` parses conventional directive comments such as `//go:generate`.
- `token.File.End` returns a file's end position.

`ast.BasicLit.ValueEnd` records an exact literal end. A tool that changes `ValuePos` must update or clear `ValueEnd` to avoid formatting differences.

The AST package-merging APIs and `parser.ParseDir` are deprecated.

Go 1.27 is scheduled to ignore `gotypesalias`, after which `go/types` will always represent aliases with `Alias`.

## Deterministic concurrency tests

### Stable API

Use `synctest.Test` from `testing/synctest` to run a test in an isolated bubble and `synctest.Wait` to wait until every other goroutine in that bubble is durably blocked. `Wait` is synchronization recognized by the race detector.

The package first appeared experimentally behind `GOEXPERIMENT=synctest` with a `Run` API and no compatibility guarantee. `Run` placed its callback and all descendant goroutines in the bubble:

```sh
GOEXPERIMENT=synctest go test ./...
```

The package is now generally available. The old `Run` remains only under that experiment in Go 1.25 and was scheduled for removal in Go 1.26. Use `Test`, not `Run`, in current code.

### Fake time and durable blocking

The `time` package uses a fake clock inside a bubble. Time advances to the next event only when every goroutine is durably blocked, making sleeps and timers deterministic without wall-clock delays.

Durable blocking includes:

- Send or receive on a nil channel or a channel created in the same bubble.
- A `select` containing only durable cases.
- `time.Sleep`.
- `sync.Cond.Wait`.
- `sync.WaitGroup.Wait`.

Mutex acquisition and external I/O are not durable. Use in-memory substitutes such as `net.Pipe` instead of real network I/O. A channel created in a bubble panics if used outside it.

The experimental `Run` API waited for all bubble goroutines to exit and panicked on a deadlock that fake-time advancement could not resolve. Always shut down background goroutines.

## Test lifecycle and output

### Test-scoped contexts

`T.Context` and `B.Context` return a context canceled after the test or benchmark finishes but before registered cleanup functions execute. Use this ordering when cleanup must observe cancellation.

### Attributes and log writers

`T.Attr`, `B.Attr`, and `F.Attr` attach key/value attributes to test logs and JSON events. Their `Output` methods return indented log writers without file-and-line prefixes.

`testing.AllocsPerRun` panics if parallel tests are running instead of returning a measurement made inherently flaky by concurrent activity.

### Persistent artifacts

`T.ArtifactDir`, `B.ArtifactDir`, and `F.ArtifactDir` return directories for test output. With `go test -artifacts`, the directory persists beneath `-outputdir`, or beneath the current directory when `-outputdir` is unset, and its location is logged on first use. Without `-artifacts`, it is temporary and removed after the test.

## Profiling tools

The `pprof -http` UI opens on the flame graph. Find the former graph view under `View -> Graph` or at `/ui/graph`.
