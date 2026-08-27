# Validation tooling and interoperability

This reference is attributed to `conformance-and-interoperability`. Use it to
build automation that distinguishes schema validity, specification
conformance, and minimum-elements policy.

## Version-aware offline validation

`sbom-utility validate` detects a JSON BOM's declared format and version and
selects the corresponding embedded schema together with imported schemas.
Supported CycloneDX and SPDX 2.x documents can therefore be checked offline.
The bundled schemas currently reach CycloneDX 1.7 and SPDX 2.3. Inspect the
exact formats, versions, and variants in the installed binary:

```shell
sbom-utility schema list -q
sbom-utility validate -i bom.json
```

Do not assume that a schema exists merely because the tool recognizes the BOM
family. Treat `schema list` output as the runtime capability record.

## Automation result contract

Every `sbom-utility` command uses:

| Exit code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Application error |
| `2` | Validation failure |

Preserve this distinction in CI and scripts. Validation errors can be emitted
as JSON. Only ten errors are formatted by default. Increase `--error-limit`
when completeness matters, and use `--error-value=false` to omit potentially
large failing values:

```shell
sbom-utility validate -i bom.json --format json \
  --error-limit 100 --error-value=false -q
```

## Alternate schemas versus custom rules

These are separate mechanisms:

- `--force` validates against a schema at an `https://` or `file://` URI.
- `--config-schema` registers a schema, selected by its `--variant` name.
- The experimental `--custom` path is CycloneDX-specific. Its rule files
  currently support `isUnique` and `hasProperties`.

```shell
sbom-utility validate -i bom.json \
  --force file:///opt/schemas/bom.json

sbom-utility validate -i bom.json \
  --config-schema config.json --variant corporate

sbom-utility validate -i bom.cdx.json --custom rules.json
```

Do not use a custom-rule file where an alternate JSON Schema is intended, or
vice versa.

## Minimum-elements conformance

`ntia-conformance-checker` checks SPDX 2.2, 2.3, and 3.0 documents against:

- The 2021 NTIA minimum elements.
- The 2024 CISA FSCT3 minimum expectation.

FSCT3 additionally requires license and copyright-holder information. Although
SPDX 3 permits multiple SBOM objects in one document, this checker currently
handles only one.

## `sbomcheck`

The package requires Python 3.10 or newer. It validates input by default;
`--skip-validation` disables that step. Its defaults are SPDX 2 and NTIA.
Select `spdx3` and `fsct3-min` explicitly when those are the intended targets.
Reports can use `print`, `quiet`, `json`, or `html`.

```shell
pip install ntia-conformance-checker
sbomcheck -s spdx3 -c fsct3-min --output json \
  --output-file report.json bom.spdx3.json
```

## Suggested CI sequence

1. Read the BOM's format and version metadata.
2. Confirm the installed validator has the matching schema.
3. Run schema validation and branch separately on application versus
   validation failure.
4. Run the format's semantic or ontology pass.
5. Run the selected NTIA or CISA minimum-elements policy.
6. If the document contains multiple SPDX 3 SBOM objects, account for the
   checker's single-SBOM limitation rather than silently treating the result as
   complete.
