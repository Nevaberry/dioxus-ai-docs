# Registries, Publishing, and Supply Chain

Use this reference for registry routing and authentication, audit and trust
policy, package packing and publishing, staged releases, signatures,
provenance, and SBOM generation.

## Registry Selection

### Scoped registry option (batch `2025-02`)

Pass a scoped registry directly as `--@scope:registry=<url>`; a
`--config.` prefix is unnecessary.

```sh
pnpm --@scope:registry=https://scope.example.com/npm install
```

### JSR packages (batch `2025-04`)

`jsr:` installs a JSR package with an optional range. A scoped JSR package is
saved under its ordinary name and becomes an npm-compatible alias when
published. `@jsr` defaults to `https://npm.jsr.io/` unless
`@jsr:registry` overrides it.

```sh
pnpm add jsr:@foo/bar
pnpm add jsr:@foo/bar@^0.1
```

### Named registries (batch `11.1-11.3`)

Use the built-in `gh:` prefix for GitHub Packages or configure
`namedRegistries`. Credentials still come from the ordinary URL-specific
`.npmrc` entry. Replace the built-in `gh` URL when using GitHub Enterprise
Server.

```yaml
namedRegistries:
  work: https://npm.work.example.com/
```

```sh
pnpm add work:@corp/lib@^2.0.0
```

Named-registry specifiers are also valid in `peerDependencies`; their embedded
ranges drive peer matching (batch `11.10-11.17`).

## Authentication and TLS

### Inline TLS material (batch `2025-12`)

Registry-URL-scoped `cert`, `ca`, and `key` values may be inline in `.npmrc`.
The older `certfile`, `cafile`, and `keyfile` settings remain the file-backed
forms.

### Credentials are destination-bound (batch `10.34.0`)

Unscoped `_authToken`, `_auth`, `username`/`_password`, `tokenHelper`, and
inline `cert`/`key` are pinned at load time to the registry specified by the
same configuration source. A later `registry=` override cannot redirect them.
Each unscoped setting emits a deprecation warning with its source and pinned
URL.

`tokenHelper` values containing environment variables are rejected
(batch `2025-12`).

### Scoped login (batch `11.1-11.3`)

`pnpm login --scope <scope>` writes a normalized `@scope:registry` mapping and
the token to the pnpm auth file. A missing leading `@` is added.

```sh
pnpm login --scope acme
```

### URL-scoped credentials from environment (batch `11.6-11.9`)

Provide URL-scoped settings through `npm_config_//…` or `pnpm_config_//…`
environment variables to avoid a project `.npmrc`. Shells reject these
characters in ordinary identifiers, so pass them with `env` or a CI secret
facility that accepts arbitrary names.

```sh
env "pnpm_config_//registry.npmjs.org/:_authToken=$NPM_TOKEN" pnpm install
```

These trusted variables override project/workspace `.npmrc` but not CLI
options. `pnpm_config_` wins over `npm_config_`.

### Different tokens for scopes on one host (batch `11.6-11.9`)

Append a package scope after the registry URL in an auth key. An unscoped
token remains the fallback:

```ini
@org-a:registry=https://npm.pkg.github.com/
@org-b:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:@org-a:_authToken=ORG_A_TOKEN
//npm.pkg.github.com/:@org-b:_authToken=ORG_B_TOKEN
//npm.pkg.github.com/:_authToken=FALLBACK_TOKEN
```

### Structured global authentication (batch `11.10-11.17`)

`_auth` can carry registry-wide key `@` and scope-specific credentials
together with the destination URL. It is accepted only from global
`config.yaml` or `pnpm_config__auth`, never from project configuration.
Global config also accepts `registries` and `namedRegistries`.

```sh
export pnpm_config__auth='{"https://registry.npmjs.org":{"@":{"authToken":"npm-token"},"@org":{"authToken":"org-token"}}}'
```

## Audit

### Exclude selected vulnerabilities (batch `2025-05-06`)

`pnpm audit --ignore-unfixable` omits advisories with no fix. Repeat
`--ignore=<CVE>` to exclude selected CVEs even when a fix exists.

```sh
pnpm audit --ignore-unfixable
pnpm audit --ignore=CVE-2021-1234 --ignore=CVE-2021-5678
```

During pnpm 11 migration, replace `auditConfig.ignoreCves` with
`auditConfig.ignoreGhsas` and translate each identifier manually
(batch `migration-10-to-11`).

### Apply fixes through updates (batch `11.0.0`)

`pnpm audit --fix=update` updates vulnerable packages in the lockfile rather
than creating overrides. `--interactive` selects advisories. Every
`pnpm audit --fix` adds each minimum patched version to
`minimumReleaseAgeExclude` so security fixes are not delayed by the age gate.

```sh
pnpm audit --fix=update --interactive
```

### Current audit configuration (batch `11.10-11.17`)

Top-level `audit` replaces `auditConfig` and `auditLevel`. Deprecated keys work
until the next major, but new values take precedence when both are present.

```yaml
audit:
  level: high
  ignore:
    - GHSA-xxxx-yyyy-zzzz
```

## Registry Signature Verification

`pnpm audit signatures` verifies installed packages against ECDSA registry
signatures and keys published at `/-/npm/v1/keys`. It follows scoped registry
selection and skips registries without signing keys (batch `11.1-11.3`).

```sh
pnpm audit signatures
```

## Trust Policy

### Reject trust downgrades (batch `2025-11`)

`trustPolicy: no-downgrade` fails when a release has weaker trust evidence than
an earlier release. `trustPolicyExclude` allows named exact versions or
`||` disjunctions.

```yaml
trustPolicy: no-downgrade
trustPolicyExclude:
  - chokidar@4.0.3
  - webpack@4.47.0 || 5.102.1
```

Policy failure remains fatal for an optional dependency. Prerelease trust
evidence is ignored when selecting a stable release.

`trustPolicyIgnoreAfter` skips trust comparisons for versions older than the
configured age (batch `2025-12`).

### Reuse a reviewed lockfile (batch `11.1-11.3`)

`trustLockfile: true` skips repeated `minimumReleaseAge` and
`trustPolicy: no-downgrade` evaluation for entries loaded from the lockfile.
It defaults false and is appropriate only when lockfile changes pass a trusted
review process.

### Evidence ranking (batch `11.4-11.5`)

Trusted-publisher metadata receives its highest rank only when provenance is
also present. Registry metadata with an `approver` field is staged-publish
evidence and ranks above trusted-publisher plus provenance evidence.

The metadata-cache lockfile-verification log survives `pnpm store prune`, so an
unchanged lockfile need not repeat these checks (batch `2026-08`).

## Packing

### Inspect and customize contents

`pnpm pack --dry-run` lists files without creating a tarball
(batch `2025-12`).

`hooks.beforePacking` runs immediately before `pnpm pack` or `publish` creates
the archive and returns the manifest to publish without changing the local
`package.json` (batch `2026-01-02`).

```js
module.exports = {
  hooks: {
    beforePacking(pkg) {
      delete pkg.devDependencies
      return pkg
    }
  }
}
```

`pnpm pack --skip-manifest-obfuscation` preserves the original
`packageManager` and publish lifecycle scripts in the output manifest. The
pnpm-specific `pnpm` field is still removed (batch `11.1-11.3`).

### Workspace and application packing

`pnpm -r pack` packs every workspace project (batch `2025-05-06`).
`pnpm pack-app` creates a Node.js single-executable application
(batch `11.0.0`).

`publishConfig.engines` overrides top-level `engines` only in the published
manifest, allowing development and consumer runtime requirements to differ
(batch `2025-11`).

## Publishing

### Archive publishing (batch `2025-09`)

`pnpm publish` accepts a package archive whose filename ends in `.tar.gz`.

### Native registry commands (batch `11.0.0`)

pnpm 11 implements `publish`, `view`, `login`, `logout`, `deprecate`,
`unpublish`, `dist-tag`, `version`, `search`, `star`, and `whoami` natively
instead of passing them to npm.

The commands `access`, `bugs`, `edit`, `issues`, `owner`, `prefix`, `profile`,
`pkg`, `repo`, `set-script`, `team`, `token`, and `xmas` initially report
“not implemented.” Native `access` and `team` are added later as described
below.

Publishing reads `PNPM_CONFIG_OTP`, prompts when OTP is required, and supports
web authentication through a QR code and URL.

`pnpm dist-tag add` and `rm` surface npmjs.org 2FA through browser
authentication when `--otp` is absent; `--otp=<code>` retains the classic flow
(batch `11.4-11.5`).

### Atomic recursive batches (batch `11.6-11.9`)

`pnpm publish --recursive --batch` submits all selected workspace packages in
one all-or-nothing request. The registry must implement pnpm's batch endpoint
or the command fails with `ERR_PNPM_BATCH_PUBLISH_UNSUPPORTED`.

### Native access and team management (batch `11.10-11.17`)

`pnpm access` manages visibility, collaborators, MFA requirements, and team
grants. `pnpm team` implements `create`, `destroy`, `add`, `rm`, and `ls` with
OTP, parseable, and JSON output.

```sh
pnpm team create @org:team --registry <url>
```

## Staged Publishing

`pnpm stage` publishes a version hidden from ordinary installs, lists or
downloads it, and either approves or rejects it (batch `11.1-11.3`).

```sh
pnpm stage publish
pnpm stage list
pnpm stage view
pnpm stage download
pnpm stage approve
pnpm stage reject
```

Staged releases with `approver` metadata rank highest in trust comparisons
(batch `11.4-11.5`).

## Software Bills of Materials

### Formats and specification versions (batches `11.0.0` and `11.1-11.3`)

`pnpm sbom` emits CycloneDX 1.7 or SPDX 2.3 JSON. For CycloneDX,
`--sbom-spec-version` accepts `1.5`, `1.6`, or `1.7` and defaults to `1.7`;
the option is invalid with other formats.

### Output routing and graph selection (batch `11.6-11.9`)

`--out` writes a named file and `--split` writes one SBOM per selected
workspace package. A single filtered package becomes the root component.
CycloneDX marks components reachable only through development dependencies as
excluded development components.

`--exclude-peers` removes peer dependencies and transitive subtrees reachable
only through peers.

### Installed versus lockfile graph (batch `2026-08`)

Ordinary `pnpm sbom` omits optional platform-specific packages unavailable on
the current platform. `--lockfile-only` describes the complete,
platform-independent graph.

Git-resolution `integrity` values are not reported as checksums because pnpm
does not verify them. Verified binary-runtime archive checksums are included.
