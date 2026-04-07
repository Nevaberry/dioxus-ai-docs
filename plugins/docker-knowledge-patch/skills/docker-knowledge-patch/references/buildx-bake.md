# Buildx & Bake (Buildx 0.31.0)

## Source Policy Enforcement with Rego

Buildx 0.31.0 introduces build policy enforcement written in [Rego](https://www.openpolicyagent.org/docs/policy-language) (Open Policy Agent's policy language). Policies control what sources and images are allowed during builds.

### Auto-loading

Buildx automatically loads a policy file alongside the Dockerfile when a matching file exists:
- `Dockerfile` → looks for `Dockerfile.rego`
- `app.Dockerfile` → looks for `app.Dockerfile.rego`

### Explicit policy

```bash
docker buildx build --policy <file.rego> .
```

### Policy authoring commands

```bash
docker buildx policy eval # evaluate a policy against a build
docker buildx policy test # run policy tests
```

### Bake integration

Bake supports a `policy` key in target configuration:

```hcl
# docker-bake.hcl
target "app" {
  dockerfile = "Dockerfile"
  policy     = "policy.rego"
}
```

Bake also auto-loads matching policy files (same naming convention as standalone buildx).

---

## Bake `--var` Flag

Set HCL variables directly from the command line instead of relying on environment variables:

```bash
docker buildx bake --var FOO=bar --var VERSION=1.2.3
```

This is equivalent to setting `FOO=bar VERSION=1.2.3` in the environment before running bake, but more explicit and portable.

---

## Bake `semvercmp` Stdlib Function

New helper function available in Bake HCL files for semantic version comparisons. Use `semvercmp` to conditionally set values based on version strings.

---

## Bake Env Lookup Disable

New option to prevent `bake` from reading host environment variables. This is useful for:
- Reproducible builds that should not depend on the host environment
- CI/CD pipelines where environment leakage is undesirable
- Ensuring all variables are explicitly passed via `--var` or defined in the HCL file
