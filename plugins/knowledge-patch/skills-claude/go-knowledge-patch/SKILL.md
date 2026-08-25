---
name: go-knowledge-patch
description: Go
version: 1.26.0
license: MIT
metadata:
  author: Nevaberry
---


# Go Knowledge Patch

Use this skill before changing Go language code, modules, build pipelines, tests,
runtime diagnostics, cryptographic code, HTTP stacks, data formats, or platform
integrations. Check the project `go` directive and relevant topic reference before
depending on defaults, experiments, or compatibility switches.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-core.md](references/language-and-core.md) | Iterators, generics, templates, errors, reflection, time, Unicode, and core APIs |
| [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md) | Modules, commands, vet, caches, source tools, synctest, artifacts, and support policy |
| [runtime-and-observability.md](references/runtime-and-observability.md) | Garbage collection, scheduling, traces, crash recovery, cleanup, heap layout, and profiles |
| [filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md) | Rooted filesystems, links, tar, JSON, JPEG, compression, Windows handles, and `fstest` |
| [networking-and-http.md](references/networking-and-http.md) | DNS, HTTP protocols, redirects, reverse proxies, CSRF, URL parsing, and MPTCP |
| [crypto-tls-and-x509.md](references/crypto-tls-and-x509.md) | FIPS, randomness, signatures, KEM and HPKE, RSA, X.509, SHA-3, and TLS defaults |
| [build-linking-and-platforms.md](references/build-linking-and-platforms.md) | Cgo, linking, build IDs, WASI, architecture profiles, SIMD, ports, and bootstrap floors |

## Breaking changes and migrations

### Remove obsolete API dependencies

- Replace `cmd/doc` and `go tool doc` with the flag-compatible `go doc`.
- Replace `httputil.ReverseProxy.Director` with `Rewrite`; `Director` can add a
  header that a client-selected hop-by-hop declaration later removes.
- Pass the block returned by `aes.NewCipher` to `crypto/cipher` constructors;
  its undocumented CTR, GCM, and CBC methods are no longer exposed.
- Replace deprecated OFB and CFB helpers with authenticated `AEAD` modes, or
  `NewCTR` only when an unauthenticated stream is unavoidable.
- Migrate from PKCS #1 v1.5 encryption and direct use of ECDSA key `big.Int`
  fields.
- Replace deprecated AST package-merging APIs and `parser.ParseDir` in source
  tooling.

### Account for stricter behavior

- Check an error before dereferencing its possibly nil result; required nil
  checks are no longer delayed.
- Bracket IPv6 literals and expect `url.Parse` to reject malformed host colons.
- Expect time parsing to reject out-of-range zone offsets.
- Reject RSA keys smaller than 1024 bits and certificates signed with SHA-1.
- Do not inject cryptographic randomness through operation arguments. Use
  `testing/cryptotest.SetGlobalRandom` when tests need deterministic randomness.
- Update golden files or cache keys that assume byte-identical JPEG or
  DEFLATE-family output.
- Make `runtime.AddCleanup` callbacks concurrency-safe.
- Never call `testing.AllocsPerRun` while parallel tests are active.
- Treat invalid UTF-8 and duplicate JSON object names as errors when using the
  v2 JSON API.

### Audit changed defaults

- Green Tea is the garbage collector; remove obsolete experiment assumptions.
- Linux `GOMAXPROCS` observes cgroup CPU bandwidth, and the runtime periodically
  refreshes its selected default on every OS.
- `net.ListenConfig` enables Multipath TCP by default where supported.
- Several post-quantum hybrid TLS exchanges are enabled by default.
- `ServeMux` trailing-slash redirects use 307, not 301.
- File-serving helpers remove caching and encoding headers from error responses.
- Closing an HTTP/1 response body may drain unread data to permit reuse.
- HTTP/2 servers honor extensible priority signals by default.
- `go mod init` deliberately chooses an older language version than a stable
  toolchain.
- AddressSanitizer performs leak detection at exit by default.
- DWARF 5 and native ELF or Mach-O build identifiers are emitted by default.
- The standard `encoding/json` API uses the v2 backend while retaining its API
  behavior apart from possible error-text changes.

## Language quick reference

### Range over iterator functions

Iterator functions use one of these push shapes:

```go
func(func() bool)
func(func(V) bool)
func(func(K, V) bool)
```

Stop producing values as soon as `yield` returns false. Prefer the named
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

For pull-style consumption, arrange for `stop` even when iteration exits early:

```go
next, stop := iter.Pull(seq)
defer stop()
for value, ok := next(); ok; value, ok = next() {
	use(value)
}
```

Select language version 1.23 or newer before using range-over-function syntax.
See [language-and-core.md](references/language-and-core.md) for iterator helpers,
generic methods, initialized `new`, templates, reflection, and errors.

## Testing and deterministic concurrency

Use stable `synctest.Test` and `synctest.Wait` from `testing/synctest`. Inside a
bubble, time advances only when every goroutine is durably blocked. Same-bubble
channel operations, timers, `sync.Cond.Wait`, and `sync.WaitGroup.Wait` can be
durable; mutex contention and external I/O are not.

Use in-memory I/O such as `net.Pipe`, make every background goroutine exit, and
do not use a channel created inside a bubble from outside it.

Prefer newer test lifecycle and diagnostic facilities where suitable:

- `T.Context` and `B.Context` for cancellation before cleanup runs.
- `T.Attr`, `B.Attr`, and `F.Attr` for structured attributes.
- `Output` for an indented log writer without source prefixes.
- `ArtifactDir` with `go test -artifacts` for persistent diagnostic output.

Read [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md)
before updating JSON event consumers, vet policy, cache integration, or source
analysis.

## Filesystem confinement

Use `os.OpenRoot` to resolve untrusted relative paths beneath a trusted directory:

```go
root, err := os.OpenRoot(base)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedName)
```

Use `os.OpenInRoot` for a one-shot open. Do not substitute `filepath.Join` plus
a pre-check; lexical checks do not prevent symlink check/use races. Consult
[filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md) for
available operations and platform limitations, including mount traversal and
`GOOS=js` behavior.

## Modules, commands, and builds

- Use the `tool` pattern to upgrade or install executable dependencies declared
  by `tool` directives; add one with `go get -tool package@version`.
- Use a `go.mod` `ignore` directive to exclude directories from package-pattern
  matching; it does not remove files from module zips.
- Use the `work` pattern for packages in the current work module or workspace.
- Consume `go build -json`, `go install -json`, and `go test -json` as evolving
  structured records, tolerating new actions and fields.
- Expect `go fix` to use analysis-based modernizers, including migrations
  driven by `//go:fix inline`.
- For modules selecting Go 1.27 or later, expect `go mod tidy` to canonicalize
  direct and indirect `require` blocks.

Read [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md)
and [build-linking-and-platforms.md](references/build-linking-and-platforms.md)
before changing CI parsers, cgo contracts, link flags, or cross-platform builds.

## Runtime and diagnostics

- Call `runtime.SetDefaultGOMAXPROCS` to restore runtime selection after an
  explicit override.
- Use `runtime/trace.FlightRecorder` to retain a recent trace window and write
  it after a significant event.
- Use the stable `goroutineleak` profile, while remembering that reachable
  synchronization primitives can hide leaks.
- Treat goroutine labels in tracebacks as potentially sensitive.
- Read scheduler population and lifetime totals from the new `/sched` metrics.
- Do not assume predictable 64-bit heap addresses.

See [runtime-and-observability.md](references/runtime-and-observability.md) for
GC selection, crash-trace recovery, cleanup diagnostics, mapping labels, and
trace listener exposure.

## Cryptography and TLS

- Use `crypto.MessageSigner` and `crypto.SignMessage` for whole-message signing.
- Use `crypto.Encapsulator`, `crypto.Decapsulator`, and `ecdh.KeyExchanger` for
  abstract or hardware-backed key exchange.
- Use `crypto/hpke` for RFC 9180 HPKE and `crypto/mldsa` for FIPS 204 ML-DSA.
- Select the cryptographic module at build time with `GOFIPS140`; select runtime
  enforcement with `GODEBUG=fips140=...`.
- Set TLS `CurvePreferences` when interoperability requires excluding default
  hybrid exchanges.
- Use `Certificate.Policies` for certificate creation and
  `VerifyOptions.CertificatePolicies` for policy-graph validation.
- Audit removed TLS, X.509, timer-channel, alias, and other `GODEBUG` escape
  hatches instead of depending on them.

Read [crypto-tls-and-x509.md](references/crypto-tls-and-x509.md) before changing
randomness, signing, RSA validation, FIPS enforcement, ECH, certificate roots,
TLS curves, or SHA-3 state handling.

## HTTP and networking

- Select HTTP/1, HTTP/2, and unencrypted HTTP/2 explicitly through
  `Server.Protocols` or `Transport.Protocols` when defaults are insufficient.
- Use `CrossOriginProtection` for Fetch Metadata-based rejection of unsafe
  cross-origin browser requests.
- Use `ReverseProxy.Rewrite`, which exposes both the unmodified inbound request
  and the outbound request.
- Expect cookies to scope to `Request.Host` when it is explicitly set.
- Inspect wrapped DNS cancellation and timeout causes with `errors.Is`.
- Disable keep-alives when a client deliberately must not reuse HTTP/1
  connections.

Read [networking-and-http.md](references/networking-and-http.md) for h2c limits,
informational responses, redirects, priority scheduling, and compatibility flags.

## Experimental and platform-sensitive features

Do not present experiments as portable or compatibility-guaranteed:

- `GOEXPERIMENT=simd` exposes portable `simd` and architecture-specific
  `simd/archsimd`, whose APIs and availability differ.
- `GOEXPERIMENT=runtimesecret` provides secret-mode execution and inheritance
  only on supported systems.

Before shipping cross-platform binaries, consult
[build-linking-and-platforms.md](references/build-linking-and-platforms.md) for
bootstrap requirements, linker layout, WASI instructions, architecture profiles,
removed or broken ports, and the PowerPC64 ELFv2 transition.
