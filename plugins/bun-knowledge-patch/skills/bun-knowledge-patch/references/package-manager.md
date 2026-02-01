# Package Manager

## Core Commands

```sh
bun outdated              # View outdated dependencies
bun update pkg --latest   # Update to latest version
bun publish               # Publish to npm (supports .npmrc, OTP)
bun list                  # Alias for bun pm ls
bun list --all            # Full transitive tree
```

## Patching

```sh
bun patch <pkg>           # Start patching
bun patch --commit <pkg>  # Save to patches/ directory
```

## Workspaces

```sh
bun run --filter='*' dev          # Run in all workspaces
bun outdated --recursive          # See outdated in all workspaces
bun update -i --recursive         # Interactive update across workspaces
bun update -i --filter="my-app"   # Scope to specific workspace
```

## Security

```sh
bun audit                          # Scan for vulnerabilities
bun audit --audit-level=high       # Only high/critical
bun audit --prod                   # Production deps only
bun audit --ignore CVE-2023-12345  # Ignore specific CVE
```

### Supply Chain Protection

```toml
# bunfig.toml
[install]
minimumReleaseAge = 604800  # 7 days in seconds
```

### Custom Security Scanner

```toml
[install.security]
scanner = "@my-company/bun-security-scanner"
```

## Dependency Analysis

```sh
bun install --analyze src/**/*.ts  # Add missing packages to package.json
bun why react                      # Trace why installed
bun why "@types/*"                 # Glob patterns supported
bun why lodash --depth=3           # Control output depth
```

## Package.json Management

```sh
bun pm pkg get name version              # Get properties
bun pm pkg set scripts.test="bun test"   # Set (dot notation)
bun pm pkg delete description            # Delete
bun pm pkg fix                           # Auto-fix errors
```

## Version Bumping

```sh
bun pm version patch                  # 0.1.0 → 0.1.1
bun pm version minor                  # 0.1.0 → 0.2.0
bun pm version major                  # 0.1.0 → 1.0.0
bun pm version 1.2.3                  # Specific version
bun pm version prerelease --preid beta  # 0.1.0 → 0.1.1-beta.0
bun pm version from-git               # From latest git tag
bun pm version --no-git-tag-version   # Skip git tag/commit
```

## Package Info

```sh
bun pm view react              # View package info
bun pm view express@4.18.2     # Specific version
bun pm view next license       # Specific property
bun pm view bun --json         # JSON output
```

## Linker Modes

```sh
bun install --linker=isolated    # pnpm-style symlinked
bun install --linker=hoisted     # Traditional flat
```

Workspaces use isolated by default for new projects. Configure:

```toml
[install]
linker = "isolated"
linkWorkspacePackages = false  # Install from registry instead of linking
```

### Selective Hoisting

```toml
[install]
publicHoistPattern = ["@types*", "*eslint*"]  # To root node_modules
hoistPattern = ["@types*"]                     # To .bun/node_modules
```

## Catalogs

Manage versions across monorepo workspaces:

```json
// root/package.json
{
  "workspaces": ["packages/*"],
  "catalog": {
    "react": "^19.0.0",
    "zod": "4.0.0-beta.1"
  }
}
```

```json
// packages/my-package/package.json
{
  "dependencies": {
    "react": "catalog:"
  }
}
```

When publishing, `catalog:` is replaced with actual version.

## Platform Filtering

```sh
bun install --os linux --cpu arm64
bun install --os darwin --os linux --cpu x64  # Multiple
bun install --os '*' --cpu '*'                # All platforms
```

## Lockfile

`bun.lock` (text-based JSONC) is default for new projects. Auto-migrates:
- `bun.lockb` (binary)
- `yarn.lock` (v1)
- `pnpm-lock.yaml`

## .npmrc Support

```ini
save-exact=true
link-workspace-packages=false
//registry.example.com/:email=user@example.com
//registry.example.com/:_authToken=xxxxx
```
