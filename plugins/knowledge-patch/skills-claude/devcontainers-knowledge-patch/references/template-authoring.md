# Template Authoring

Source batch: `template-authoring`.

## Package layout and identity

A Template directory has the manifest at its root and the Dev Container
configuration beneath `.devcontainer`:

```text
template/
├── devcontainer-template.json
└── .devcontainer/
    └── devcontainer.json
```

Boilerplate, lifecycle scripts, and other supporting files are packaged beside
them. The manifest `id` must match the Template directory name and be unique
within its repository or published package.

## Whole-template option substitution

Supporting tools prompt for values from the manifest's `options`. They then
replace every `${templateOption:<optionId>}` occurrence with the selected or
default value throughout every file before copying the Template into a project.

```json
{
  "options": {
    "imageVariant": {
      "type": "string",
      "default": "17-bullseye"
    }
  }
}
```

The substitution can appear in `devcontainer.json`:

```json
{
  "image": "mcr.microsoft.com/devcontainers/java:0-${templateOption:imageVariant}"
}
```

It also applies to all other text files in the package, not only JSON.

## Optional output paths

Before applying a Template, tooling must prompt whether to include each entry in
`optionalPaths`.

Paths are relative to the Template root:

- A file uses its exact path.
- A directory uses a trailing `/*` and includes its contents recursively.

```json
{
  "optionalPaths": [
    "GETTING-STARTED.md",
    ".github/*"
  ]
}
```

## OCI references

A published Template is addressed as:

```text
<oci-registry>/<namespace>/<template>[:<semantic-version>]
```

The registry must implement OCI Artifact Distribution. For example:

```text
ghcr.io/user/repo/go:1
```
