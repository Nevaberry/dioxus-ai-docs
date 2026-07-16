---
name: go-knowledge-patch
description: Go 1.26.0 compatibility. Use for Go work.
license: MIT
version: 1.26.0
metadata:
  author: Nevaberry
---

# Go Knowledge Patch

Use this skill before changing Go source, modules, build pipelines, tests, cryptographic code, HTTP stacks, or platform integrations. Check the relevant topic reference before relying on older defaults or compatibility switches.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-core.md](references/language-and-core.md) | Function iterators, templates, language syntax, errors, reflection, time, and regular expressions |
| [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md) | Modules, workspaces, `go` commands, vet, caches, source analysis, testing, and profiling |
| [runtime-and-observability.md](references/runtime-and-observability.md) | Garbage collection, scheduling, traces, crash recovery, cleanup, heap layout, and metrics |
| [filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md) | Rooted filesystems, links, tar, JSON v2, JPEG, Windows handles, and `fstest` |
| [networking-and-http.md](references/networking-and-http.md) | DNS, HTTP protocols, redirects, reverse proxies, CSRF, URL parsing, and MPTCP |
| [crypto-tls-and-x509.md](references/crypto-tls-and-x509.md) | FIPS, randomness, signatures, KEM and HPKE, RSA, X.509, SHA-3, and TLS defaults |
| [build-linking-and-platforms.md](references/build-linking-and-platforms.md) | Cgo, linker behavior, build IDs, process handles, WASI, architecture profiles, ports, and bootstrap floors |

## Breaking changes and deprecations

### Update removed or superseded APIs

- Replace `go tool doc` or `cmd/doc` with the flag-compatible `go doc` command.
- Replace `httputil.ReverseProxy.Director` with `Rewrite`; `Director` can add headers that a client-selected hop-by-hop declaration subsequently removes.
- Stop depending on undocumented CTR, GCM, or CBC methods of the concrete block returned by `aes.NewCipher`; use `crypto/cipher` constructors.
- Replace deprecated OFB and CFB helpers with authenticated `AEAD` modes, or `NewCTR` only when unauthenticated streaming is unavoidable.
- Migrate away from PKCS #1 v1.5 encryption and from direct use of the `big.Int` fields of ECDSA keys.
- Replace deprecated AST package-merging APIs and `parser.ParseDir` in source tools.

### Account for stricter behavior

- Check a call's error before dereferencing its possibly nil result. Nil-pointer checks now occur at the required dereference point rather than being delayed.
- Expect `url.Parse` to reject malformed hosts with ambiguous colons; bracket IPv6 literals.
- Expect `time.Parse` and `time.ParseInLocation` to reject out-of-range zone offsets.
- Expect RSA operations to reject keys smaller than 1024 bits and X.509 verification to reject SHA-1 signatures.
- Do not assume caller-supplied randomness drives DSA, ECDH, RSA, ECDSA, `rand.Prime`, or all Ed25519 key generation. Use `testing/cryptotest.SetGlobalRandom` for deterministic tests.
- Update golden files or cache keys that assume byte-identical JPEG encoding.
- Treat `runtime.AddCleanup` callbacks as concurrent and potentially parallel.
- Expect `testing.AllocsPerRun` to panic when parallel tests are active.

### Audit defaults that changed

- Green Tea is the default garbage collector; use `GOEXPERIMENT=nogreenteagc` only as a temporary diagnostic escape hatch.
- Linux `GOMAXPROCS` now observes cgroup CPU bandwidth and the runtime periodically refreshes its default on every OS.
- `net.ListenConfig` enables Multipath TCP by default where supported.
- New post-quantum hybrid TLS exchanges are enabled by default unless `CurvePreferences` or the applicable `GODEBUG` setting disables them.
- `ServeMux` trailing-slash redirects use status 307, not 301.
- `ServeContent`, `ServeFile`, and `ServeFileFS` strip caching and encoding headers from error responses.
- `go mod init` deliberately selects an older language version than the running stable toolchain.
- `go build -asan` performs leak detection at process exit by default.
- DWARF 5 and native ELF/Mach-O build identifiers are emitted by default.

## Language and iterator quick reference

### Range over iterator functions

Use one of these push-iterator shapes:

```go
func(func() bool)
func(func(V) bool)
func(func(K, V) bool)
```

Stop producing values as soon as `yield` returns false. Prefer the named `iter.Seq[V]` and `iter.Seq2[K, V]` forms; there is no `Seq0`.

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

For pull-style consumption, call `iter.Pull` and arrange for `stop` even when iteration exits early:

```go
next, stop := iter.Pull(seq)
defer stop()
for value, ok := next(); ok; value, ok = next() {
	use(value)
}
```

Select language version 1.23 or newer before using range-over-function syntax. See [language-and-core.md](references/language-and-core.md) for `slices`, `maps`, templates, reflection iterators, initialized `new`, and self-referential constraints.

Use `errors.AsType[E]` for type-safe extraction from wrapped error chains.

## Testing and deterministic concurrency

Use stable `synctest.Test` and `synctest.Wait` from `testing/synctest` for fake-time concurrency tests. Inside a synctest bubble, time advances only when every goroutine is durably blocked. Channel operations, timers, `sync.Cond.Wait`, and `sync.WaitGroup.Wait` can be durable; mutex contention and external I/O are not.

Use in-memory I/O such as `net.Pipe`, ensure every background goroutine exits, and remember that a channel created inside a bubble cannot be used outside it.

Use these newer test facilities where appropriate:

- `T.Context` and `B.Context` for cancellation before cleanup runs.
- `T.Attr`, `B.Attr`, and `F.Attr` for structured attributes.
- `Output` for an indented log writer without source prefixes.
- `ArtifactDir` with `go test -artifacts` for persistent diagnostic output.

See [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md) for exact lifecycle, JSON event, vet, and artifact rules.

## Filesystem confinement

Use `os.OpenRoot` when resolving untrusted relative paths beneath a trusted directory:

```go
root, err := os.OpenRoot(base)
if err != nil {
	return err
}
defer root.Close()

file, err := root.Open(untrustedName)
```

Use `os.OpenInRoot` for a one-shot open. Do not replace it with `filepath.Join` plus a pre-check: lexical checks do not prevent symlink check/use races. Read [filesystem-data-and-encoding.md](references/filesystem-data-and-encoding.md) for available methods and platform limitations, especially mount traversal and `GOOS=js` behavior.

## Modules, commands, and build output

- Use the `tool` meta-pattern to upgrade or install every executable dependency declared with a `tool` directive.
- Use `go get -tool package@version` to add both the tool directive and its module dependency.
- Use a `go.mod` `ignore` directive to exclude directories from package-pattern matching; it does not remove files from module zips.
- Use the `work` pattern to select all packages in the current work module or workspace.
- Consume `go build -json` and `go install -json` as structured records; `go test -json` can interleave build and test actions.
- Expect `go fix` to apply analysis-based modernizers, including migrations driven by `//go:fix inline`.

See [tooling-modules-and-testing.md](references/tooling-modules-and-testing.md) before updating CI parsers, vanity imports, private-module authentication, caches, or source-analysis tools.

## Runtime and diagnostics

- Call `runtime.SetDefaultGOMAXPROCS` to return to the runtime-selected value after an explicit override.
- Use `runtime/trace.FlightRecorder` to retain a recent in-memory trace window and write it after a significant event.
- Use the experimental `goroutineleak` profile only with `GOEXPERIMENT=goroutineleakprofile`; understand that reachable synchronization primitives can hide leaks.
- Read the `/sched/goroutines`, `/sched/threads:threads`, and `/sched/goroutines-created:goroutines` metrics for scheduler population and lifetime creation counts.
- Treat assumptions about predictable 64-bit heap addresses as invalid.

See [runtime-and-observability.md](references/runtime-and-observability.md) for GC selection, trace recovery, mapping labels, cleanup checks, and experiment controls.

## Cryptography and TLS

### Prefer current abstractions

- Use `crypto.MessageSigner` and `crypto.SignMessage` when a key signs whole messages.
- Use `crypto.Encapsulator`, `crypto.Decapsulator`, and `ecdh.KeyExchanger` for abstract or hardware-backed key exchange.
- Use `crypto/hpke` for RFC 9180 HPKE, including supported post-quantum hybrid KEMs.

### Check policy and compatibility

- Choose the cryptographic module at build time with `GOFIPS140`; enable runtime FIPS mode through `GODEBUG=fips140=...`.
- Set TLS `CurvePreferences` when interoperability requires explicitly excluding a default hybrid exchange.
- Populate X.509 creation policies through `Certificate.Policies`, and use `VerifyOptions.CertificatePolicies` when policy graph validation is required.
- Never assume legacy TLS and X.509 `GODEBUG` switches remain available indefinitely; several are scheduled to be ignored or removed.

Read [crypto-tls-and-x509.md](references/crypto-tls-and-x509.md) before changing randomness injection, signing, RSA validation, FIPS enforcement, ECH, TLS curves, certificate policies, or SHA-3 state handling.

## HTTP and networking

- Configure HTTP/1, HTTP/2, and unencrypted HTTP/2 explicitly with `Server.Protocols` or `Transport.Protocols` when defaults are insufficient.
- Use `CrossOriginProtection` for Fetch Metadata-based rejection of unsafe cross-origin browser requests.
- Use `ReverseProxy.Rewrite`, which exposes the unmodified inbound request and the outbound request.
- Expect cookies to scope to `Request.Host` when it is explicitly set.
- Inspect wrapped DNS cancellation and timeout causes with `errors.Is`.

Read [networking-and-http.md](references/networking-and-http.md) for h2c constraints, informational responses, strict host parsing, redirects, and compatibility flags.

## Experimental and platform-sensitive features

Do not present experimental packages as portable or compatibility-guaranteed:

- `GOEXPERIMENT=jsonv2` exposes `encoding/json/v2` and `encoding/json/jsontext`.
- `GOEXPERIMENT=simd` exposes non-portable amd64 `simd/archsimd` operations.
- `GOEXPERIMENT=runtimesecret` is limited to Linux amd64 and arm64.
- `GOEXPERIMENT=goroutineleakprofile` enables leak profiling.

Before shipping cross-platform binaries, consult [build-linking-and-platforms.md](references/build-linking-and-platforms.md) for changed bootstrap requirements, linker layout, WASI requirements, architecture feature profiles, removed or broken ports, and WebAssembly instruction floors.
