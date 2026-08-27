---
name: go-knowledge-patch
description: Go
version: "1.26.0"
license: MIT
metadata:
  author: Nevaberry
---


# Go Knowledge Patch

Use this skill before changing Go source, modules, build pipelines, tests,
cryptographic code, HTTP stacks, runtime integrations, or platform-specific
builds. Read the relevant topic reference before relying on older defaults,
removed commands, compatibility switches, or byte-for-byte encoded output.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-core.md](references/language-and-core.md) | Language syntax, iterators, templates, errors, reflection, source positions, time, regular expressions, and Unicode |
| [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md) | Modules, workspaces, `go` commands, vet, caches, source modernization, testing, and profiling tools |
| [runtime-and-observability.md](references/runtime-and-observability.md) | Garbage collection, scheduling, traces, crash recovery, cleanup, heap layout, and runtime metrics |
| [filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md) | Rooted filesystems, links, tar, JSON, compression, JPEG, UUIDs, Windows handles, and `fstest` |
| [networking-and-http.md](references/networking-and-http.md) | DNS, HTTP protocols, redirects, reverse proxies, CSRF, URL parsing, MPTCP, and connection reuse |
| [crypto-tls-and-x509.md](references/crypto-tls-and-x509.md) | FIPS, randomness, signing, KEM and HPKE, RSA, X.509, SHA-3, TLS defaults, and certificate roots |
| [build-linking-and-platforms.md](references/build-linking-and-platforms.md) | Cgo, linker behavior, build IDs, sanitizers, WASI, architecture profiles, ports, SIMD, and bootstrap floors |

## Breaking changes and deprecations

### Replace removed and unsafe APIs

- Replace `go tool doc` and `cmd/doc` with `go doc`. It also accepts
  `package@version`; use `-ex` to list executable examples.
- Replace `httputil.ReverseProxy.Director` with `Rewrite`. A client-selected
  hop-by-hop declaration can remove headers added by `Director`.
- Stop calling undocumented CTR, GCM, or CBC methods on the concrete block
  returned by `aes.NewCipher`; use `crypto/cipher` constructors.
- Replace deprecated OFB and CFB helpers with authenticated `AEAD` modes, or
  `NewCTR` only when unauthenticated streaming is unavoidable.
- Migrate away from PKCS #1 v1.5 encryption and direct use of ECDSA key
  `big.Int` fields.
- Replace deprecated AST package-merging APIs and `parser.ParseDir` in source
  tools.

### Account for stricter behavior

- Check a call's error before dereferencing its result. Required nil checks
  happen at the dereference rather than being delayed.
- Expect `url.Parse` to reject malformed hosts with ambiguous colons; bracket
  IPv6 literals.
- Expect `time.Parse` and `time.ParseInLocation` to reject out-of-range zone
  offsets.
- Expect RSA operations to reject keys smaller than 1024 bits and X.509
  verification to reject SHA-1 signatures.
- Do not assume caller-supplied randomness controls DSA, ECDH, RSA, ECDSA,
  `rand.Prime`, or every Ed25519 key-generation path. Use
  `testing/cryptotest.SetGlobalRandom` for deterministic tests.
- Update golden files and cache keys that require byte-identical JPEG or
  DEFLATE-family output.
- Treat `runtime.AddCleanup` callbacks as concurrent and potentially parallel.
- Expect `testing.AllocsPerRun` to panic while parallel tests are active.
- Treat unknown fields such as `OutputType` in `go test -json` records as
  forward-compatible structured data.

### Audit changed defaults

- Green Tea is the default garbage collector. Use
  `GOEXPERIMENT=nogreenteagc` only as a temporary diagnostic escape hatch
  where the selected toolchain still supports it.
- Linux `GOMAXPROCS` observes cgroup CPU bandwidth, and the runtime periodically
  refreshes its default on every OS.
- `net.ListenConfig` enables Multipath TCP by default where supported.
- Post-quantum hybrid TLS exchanges are enabled by default unless
  `CurvePreferences` or the applicable `GODEBUG` switch disables them.
- `ServeMux` trailing-slash redirects use status 307.
- `ServeContent`, `ServeFile`, and `ServeFileFS` strip caching and encoding
  headers from error responses.
- Closing an HTTP/1 response body may drain unread data to preserve connection
  reuse; disable keep-alives when reuse is intentionally unwanted.
- `go mod init` deliberately selects an older language version than the stable
  toolchain executing it.
- `go build -asan` performs leak detection at process exit by default.
- DWARF 5 and native ELF or Mach-O build identifiers are emitted by default.
- The JSON v2 implementation backs `encoding/json`; it rejects invalid UTF-8
  and duplicate object names through the v2 APIs.

## Language quick reference

### Range over iterator functions

Use one of these push-iterator shapes:

```go
func(func() bool)
func(func(V) bool)
func(func(K, V) bool)
```

Stop producing values when `yield` returns false. Prefer the named
`iter.Seq[V]` and `iter.Seq2[K, V]` forms; there is no `Seq0`.

```go
func (s *Set[E]) All() iter.Seq[E] {
	return func(yield func(E) bool) {
		for value := range s.m {
			if !yield(value) {
				return
			}
		}
	}
}
```

For pull-style consumption, call `iter.Pull` and always arrange for `stop`
when iteration can end early:

```go
next, stop := iter.Pull(seq)
defer stop()
for value, ok := next(); ok; value, ok = next() {
	use(value)
}
```

Select language version 1.23 or newer before using range-over-function syntax.
See [language-and-core.md](references/language-and-core.md) for iterator helpers,
templates, reflection iterators, initialized `new`, self-referential
constraints, and generic-method limitations.

### Newer generic forms

Methods on non-parameterized receiver types may declare type parameters, but a
parameterized receiver cannot add them and generic methods cannot implement
interface methods. Generic function values also participate in type inference
when assigned or converted to a matching function type.

Use `errors.AsType[E]` for type-safe extraction from a wrapped error chain.

## Testing and deterministic concurrency

Use stable `synctest.Test` and `synctest.Wait` from `testing/synctest` for
fake-time concurrency tests. Inside a synctest bubble, time advances only when
every goroutine is durably blocked. Channel operations, timers,
`sync.Cond.Wait`, and `sync.WaitGroup.Wait` can be durable; mutex contention
and external I/O are not.

Use in-memory I/O such as `net.Pipe`, ensure every background goroutine exits,
and do not use a channel created inside a bubble outside it.

Use these test facilities where appropriate:

- `T.Context` and `B.Context` for cancellation before cleanup runs.
- `T.Attr`, `B.Attr`, and `F.Attr` for structured attributes.
- `Output` for an indented log writer without source prefixes.
- `ArtifactDir` with `go test -artifacts` for persistent diagnostic output.

## Filesystem confinement

Use `os.OpenRoot` when resolving untrusted relative paths beneath a trusted
directory:

```go
root, err := os.OpenRoot(base)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedName)
```

Use `os.OpenInRoot` for a one-shot open. Do not replace it with
`filepath.Join` plus a pre-check: lexical checks do not prevent symlink
check/use races. Read
[filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md)
for available methods and platform limitations, especially mount traversal
and `GOOS=js` behavior.

## Modules, commands, and build output

- Use the `tool` meta-pattern to upgrade or install every executable dependency
  declared with a `tool` directive.
- Use `go get -tool package@version` to add both the tool directive and module
  dependency.
- Use a `go.mod` `ignore` directive to exclude directories from package-pattern
  matching; it does not remove files from module zips.
- Use the `work` pattern for all packages in the work module or workspace.
- Consume `go build -json`, `go install -json`, and `go test -json` as
  extensible structured records.
- Expect `go fix` to apply analysis-based modernizers, including migrations
  driven by `//go:fix inline`.
- For modules declaring language version 1.27 or later, expect `go mod tidy` to
  canonicalize duplicate `require` blocks.

## Runtime and diagnostics

- Call `runtime.SetDefaultGOMAXPROCS` to return to the runtime-selected value
  after an explicit override.
- Use `runtime/trace.FlightRecorder` to retain a recent in-memory trace window
  and write it after a significant event.
- Use the stable `goroutineleak` profile while understanding that reachable
  synchronization primitives can hide leaks.
- Read `/sched/goroutines`, `/sched/threads:threads`, and
  `/sched/goroutines-created:goroutines` for scheduler population and lifetime
  creation counts.
- Treat assumptions about predictable 64-bit heap addresses as invalid.
- Treat goroutine labels in tracebacks as potentially sensitive and use
  `GODEBUG=tracebacklabels=0` when they must be suppressed.

## Cryptography, TLS, and HTTP

- Use `crypto.MessageSigner` and `crypto.SignMessage` when a key signs whole
  messages.
- Use `crypto.Encapsulator`, `crypto.Decapsulator`, and `ecdh.KeyExchanger` for
  abstract or hardware-backed key exchange.
- Use `crypto/hpke` for RFC 9180 HPKE and `crypto/mldsa` for FIPS 204 ML-DSA.
- Choose the cryptographic module at build time with `GOFIPS140`; enable runtime
  FIPS mode through `GODEBUG=fips140=...`.
- Configure HTTP/1, HTTP/2, and h2c explicitly with `Server.Protocols` or
  `Transport.Protocols` when defaults are insufficient.
- Use `CrossOriginProtection` for Fetch Metadata-based rejection of unsafe
  cross-origin browser requests.
- Use `ReverseProxy.Rewrite`, which exposes both the unmodified inbound request
  and the outbound request.

## Experimental and platform-sensitive features

Do not present experimental packages as portable or compatibility-guaranteed:

- `GOEXPERIMENT=simd` exposes portable `simd` and architecture-specific
  `simd/archsimd` APIs whose details remain toolchain-sensitive.
- `GOEXPERIMENT=runtimesecret` exposes `runtime/secret`; platform support and
  inheritance behavior must be checked against the selected toolchain.

Before shipping cross-platform binaries, consult
[build-linking-and-platforms.md](references/build-linking-and-platforms.md) for
bootstrap requirements, linker layout, WASI requirements, architecture feature
profiles, ABI transitions, removed ports, and WebAssembly instruction floors.
