# Template Authoring

## Package layout and identity

A Template folder has this minimum layout:

```text
template/
├── devcontainer-template.json
└── .devcontainer/
    └── devcontainer.json
```

Package supporting files, including boilerplate and lifecycle scripts,
alongside them. The manifest `id` must match the Template directory name and
must be unique within its repository or published package.

## Whole-template option substitution

Supporting tools prompt for values described by the manifest's `options`.
Before copying the Template into the project, replace every occurrence of
`${templateOption:<optionId>}` in every file with the selected or default
value.

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

```json
{
  "image": "mcr.microsoft.com/devcontainers/java:0-${templateOption:imageVariant}"
}
```

Substitution is whole-template behavior, not a transformation limited to
`devcontainer.json`.

## Optional output paths

Before applying a Template, prompt whether to include each path listed in
`optionalPaths`. Interpret paths relative to the Template root.

- Name a file by its exact relative path.
- Name a directory with a trailing `/*` to include its contents recursively.

```json
{
  "optionalPaths": [
    "GETTING-STARTED.md",
    ".github/*"
  ]
}
```

## OCI references

Locate a published Template through an OCI registry that implements OCI
Artifact Distribution. Use:

```text
<oci-registry>/<namespace>/<template>[:<semantic-version>]
```

For example:

```text
ghcr.io/user/repo/go:1
```
