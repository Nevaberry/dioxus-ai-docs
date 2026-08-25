# Dependency Security, Audit, Trust, and SBOMs

## Audit vulnerability exclusions (2025-05-06)

`pnpm audit --ignore-unfixable` excludes vulnerabilities without fixes. Repeat `--ignore` to exclude selected CVEs even when fixes exist.

```sh
pnpm audit --ignore-unfixable
pnpm audit --ignore=CVE-2021-1234 --ignore=CVE-2021-5678
```

## Minimum release age (2025-09, 2025-10)

`minimumReleaseAge` blocks a version until the configured minutes have elapsed since publication. `minimumReleaseAgeExclude` bypasses the delay for named packages and, as of pnpm 10.17, package patterns. Exact requests remain gated with cached metadata, and a too-new stable dist-tag does not fall back to a prerelease.

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeExclude:
  - webpack
  - "@eslint/*"
```

Exclusions also accept exact versions and `||` disjunctions.

```yaml
minimumReleaseAgeExclude:
  - nx@21.6.5
  - webpack@4.47.0 || 5.102.1
```

`pnpm outdated` respects the maturity policy. If `latest` is too new, pnpm selects the highest mature version even when it is in another major.

## Trust downgrade policy (2025-11, 2025-12)

`trustPolicy: no-downgrade` fails installation when a release has weaker trust evidence than earlier releases. `trustPolicyExclude` permits named versions. Failures remain fatal for optional dependencies; prerelease evidence is ignored for stable releases.

```yaml
trustPolicy: no-downgrade
trustPolicyExclude:
  - chokidar@4.0.3
  - webpack@4.47.0 || 5.102.1
```

`trustPolicyIgnoreAfter` skips trust checks for versions published more than the configured age ago.

## Block exotic transitive sources (2025-12)

`blockExoticSubdeps` rejects exotic transitive sources such as `git+ssh:` repositories and direct HTTPS tarballs. Direct dependencies may still use them.

```yaml
blockExoticSubdeps: true
```

## Audit migration to GHSA identifiers (migration-10-to-11)

`auditConfig.ignoreCves` is replaced by `auditConfig.ignoreGhsas`. The codemod renames the key but cannot translate entries; manually replace each CVE with the GHSA in the **More info** column of `pnpm audit`.

```yaml
auditConfig:
  ignoreGhsas:
    - GHSA-xxxx-xxxx-xxxx
```

## pnpm 11 audit fixes (11.0.0)

`pnpm audit --fix=update` updates vulnerable lockfile packages instead of creating overrides; `--interactive` selects advisories. Any `pnpm audit --fix` adds each minimum patched version to `minimumReleaseAgeExclude` so the default age gate does not delay the fix.

```sh
pnpm audit --fix=update --interactive
```

## Verify registry signatures (11.1-11.3)

`pnpm audit signatures` verifies installed packages against ECDSA registry signatures and keys at `/-/npm/v1/keys`. It respects scoped registries and skips registries without signing keys.

```sh
pnpm audit signatures
```

## CycloneDX specification versions (11.1-11.3)

For `pnpm sbom --sbom-format cyclonedx`, `--sbom-spec-version` accepts `1.5`, `1.6`, or `1.7`; the default is `1.7`. The option is invalid for other formats.

```sh
pnpm sbom --sbom-format cyclonedx --sbom-spec-version 1.6
```

## Trust a reviewed lockfile (11.1-11.3)

`trustLockfile: true` skips reapplying `minimumReleaseAge` and `trustPolicy: no-downgrade` to lockfile entries. It defaults to `false` and is intended for lockfiles whose changes pass a trusted review process.

```yaml
trustLockfile: true
```

## Resolution and patch hardening (11.4-11.5)

- Git resolution `commit` must be a 40-character hexadecimal SHA; pnpm rejects other values before invoking Git.
- Patch `diff --git` headers cannot refer outside the patched package, including writes, deletes, or renames.
- Dependency aliases with path-traversal segments are rejected when reading manifests and linking `node_modules`.

## Trust evidence ranking (11.4-11.5)

Trusted-publisher metadata receives its highest trust rank only with provenance. Registry metadata containing `approver` is staged-publish evidence and ranks above trusted publishers and provenance attestations.

## Write and split SBOM output (11.6-11.9)

`pnpm sbom --out` writes a file; `--split` writes one SBOM per selected workspace package. A single filtered package becomes the root component. CycloneDX marks components reachable only through development dependencies as excluded development components.

```sh
pnpm sbom --out sbom.json
pnpm sbom --split
```

`pnpm sbom --exclude-peers` omits peer dependencies and transitive subtrees reachable only through them.

```sh
pnpm sbom --exclude-peers
```

## Release-age filtering and resolution mode (2026-08)

With `minimumReleaseAge`, `resolutionMode: lowest-direct` and `resolutionMode: time-based` select the lowest satisfying direct-dependency version rather than being forced to the highest.

```yaml
minimumReleaseAge: 1440
resolutionMode: lowest-direct
```

## Metadata cache and trust log (2026-08)

`pnpm cache path` prints the metadata-cache directory, which CI may cache with its lockfile verification log. `pnpm store prune` preserves that log, so an unchanged lockfile does not need supply-chain policies rechecked after pruning.

```sh
pnpm cache path
```

## Installed versus lockfile-only SBOMs (2026-08)

`pnpm sbom` omits optional platform-specific packages that cannot install on the current platform. `pnpm sbom --lockfile-only` describes the full platform-independent graph. Git-resolution `integrity` values are not reported as checksums because pnpm does not verify them; verified binary-runtime archive checksums are included.

```sh
pnpm sbom
pnpm sbom --lockfile-only
```
