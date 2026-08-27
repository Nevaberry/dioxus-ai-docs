# Registries, Authentication, Globals, and Publishing

## Scoped registry CLI settings (2025-02)

Pass a scoped registry directly as `--@scope:registry=...`; the `--config.` prefix is unnecessary.

```sh
pnpm --@scope:registry=https://scope.example.com/npm install
```

## JSR dependencies (2025-04)

The `jsr:` protocol installs JSR packages with an optional version range. A scoped dependency is stored under its ordinary package name and converted to an npm-compatible alias when publishing. `@jsr` defaults to `https://npm.jsr.io/` unless `@jsr:registry` is configured.

```sh
pnpm add jsr:@foo/bar
pnpm add jsr:@foo/bar@^0.1
```

```json
{
  "dependencies": {
    "@foo/bar": "jsr:^0.1.2"
  }
}
```

## Publish package archives (2025-09)

`pnpm publish` accepts a package archive whose filename ends in `.tar.gz`.

```sh
pnpm publish ./package.tar.gz
```

## Published engine requirements (2025-11)

`publishConfig.engines` overrides top-level `engines` during publishing, so published runtime requirements may differ from development requirements.

```json
{
  "engines": { "node": ">=24" },
  "publishConfig": { "engines": { "node": ">=20" } }
}
```

## Inline TLS material (2025-12)

pnpm 10.25 accepts inline registry-scoped `cert`, `ca`, and `key` values in `.npmrc`, in addition to `certfile`, `cafile`, and `keyfile`.

```ini
//registry.example.com/:ca=-----BEGIN CERTIFICATE-----...
```

## Pack previews (2025-12)

`pnpm pack --dry-run` lists files that would enter the tarball without creating it.

```sh
pnpm pack --dry-run
```

## Token helper restriction (2025-12)

pnpm 10.27 errors if `tokenHelper` or registry-scoped `<url>:tokenHelper` contains an environment variable.

## Staged publishing (11.1-11.3)

`pnpm stage` publishes a version hidden from ordinary installs, then lets you inspect, download, promote, or discard it.

```sh
pnpm stage publish
pnpm stage list
pnpm stage view
pnpm stage download
pnpm stage approve
pnpm stage reject
```

## Named registries (11.1-11.3)

Dependencies may use the built-in `gh:` prefix for GitHub Packages or a name from `namedRegistries`. Authentication still comes from the registry URL's `.npmrc` entry. The built-in `gh` mapping may be replaced for GitHub Enterprise Server.

```yaml
namedRegistries:
  work: https://npm.work.example.com/
```

```sh
pnpm add work:@corp/lib@^2.0.0
```

## Scoped registry login (11.1-11.3)

`pnpm login --scope <scope>` writes a normalized `@scope:registry` mapping with the token in the pnpm auth file. A missing leading `@` is added automatically.

```sh
pnpm login --scope acme
```

## Preserve manifest metadata when packing (11.1-11.3)

`pnpm pack` and `pnpm publish` accept `--skip-manifest-obfuscation` to retain the original `packageManager` field and publish lifecycle scripts in the output manifest. The pnpm-specific `pnpm` field is still removed.

```sh
pnpm pack --skip-manifest-obfuscation
```

## Credential pinning (10.34.0)

Unscoped `_authToken`, `_auth`, `username`/`_password`, `tokenHelper`, and inline `cert`/`key` settings are pinned at load time to the registry declared in the same config source. A later `registry=` override cannot redirect them. Each unscoped setting emits a deprecation warning identifying its source and pinned URL.

## Browser-based 2FA for dist-tags (11.4-11.5)

Against npmjs.org, `pnpm dist-tag add` and `pnpm dist-tag rm` surface an OTP challenge through browser authentication when `--otp` is omitted. Passing `--otp=<code>` retains the classic flow.

## URL-scoped environment authentication (11.6-11.9)

Supply URL-scoped registry settings through `npm_config_//…` or `pnpm_config_//…` environment variables. Since shells reject these names as identifiers, pass them with `env` or CI support for arbitrary names. Trusted values override project/workspace `.npmrc`, not CLI options; `pnpm_config_` wins over `npm_config_`.

```sh
env "pnpm_config_//registry.npmjs.org/:_authToken=$NPM_TOKEN" pnpm install
```

## Scope-specific tokens on one registry (11.6-11.9)

Authentication keys may include a package scope after the registry URL. An unscoped token remains the fallback.

```ini
@org-a:registry=https://npm.pkg.github.com/
@org-b:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:@org-a:_authToken=ORG_A_TOKEN
//npm.pkg.github.com/:@org-b:_authToken=ORG_B_TOKEN
//npm.pkg.github.com/:_authToken=FALLBACK_TOKEN
```

## Atomic recursive publishing (11.6-11.9)

`pnpm publish --recursive --batch` sends every selected workspace package in one all-or-nothing request. The registry must implement pnpm's batch-publish endpoint or the command fails with `ERR_PNPM_BATCH_PUBLISH_UNSUPPORTED`.

```sh
pnpm publish --recursive --batch
```

## Native `view` default (11.6-11.9)

`pnpm view` without a package name searches upward for the nearest manifest and queries the package named there.

## Structured registry authentication (11.10-11.17)

`_auth` carries registry-wide (`@`) and scope-specific credentials together with their destination URL. It is accepted only from global `config.yaml` or `pnpm_config__auth`, never project files. Global config also accepts `registries` and `namedRegistries`.

```sh
export pnpm_config__auth='{"https://registry.npmjs.org":{"@":{"authToken":"npm-token"},"@org":{"authToken":"org-token"}}}'
```

## Native access and team administration (11.10-11.17)

`pnpm access` manages package visibility, collaborators, MFA requirements, and team grants. `pnpm team` supports `create`, `destroy`, `add`, `rm`, and `ls`, with OTP, parseable, and JSON output.

```sh
pnpm team create @org:team --registry <url>
```
