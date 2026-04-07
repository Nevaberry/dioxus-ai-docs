# Package Management & Config

## `links` — Local npm Package Overrides (2.3+, renamed in 2.4)

Override npm packages with local versions using `"links"` in deno.json (formerly `"patch"` in 2.3):
```json
{ "links": ["../path/to/local_npm_package"] }
```
Requires `"nodeModulesDir": "auto"` or `"manual"`. The package name must exist in the npm registry. `"patch"` still works but shows a deprecation warning.

## Registry Flags for `deno add` (2.3+)

`--npm` and `--jsr` flags to add multiple packages from one registry:
```bash
deno add --npm chalk react
deno add --jsr @std/fs @std/path
```

## `minimumDependencyAge` (2.6+)

Prevent installing newly published packages:
```json
{ "minimumDependencyAge": "P2D" }
```
Accepts minutes (`"120"`), ISO-8601 duration (`"P2D"`), or RFC3339 timestamp.

## `jsr:` Scheme in `package.json` (2.7+)

Use JSR packages directly in package.json without needing deno.json:
```json
{ "dependencies": { "@std/path": "jsr:^1.0.9" } }
```

## `package.json` Overrides (2.7+)

Deno now supports the `overrides` field to pin transitive dependency versions.

## `"publish": false` in deno.json (2.6+)

Prevent accidental JSR publishes of private/internal packages.
