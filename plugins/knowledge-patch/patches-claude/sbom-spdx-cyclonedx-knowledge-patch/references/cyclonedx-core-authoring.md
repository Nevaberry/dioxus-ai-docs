# CycloneDX core authoring

Use this reference for BOM identity, component and service modeling, licensing,
dependencies, evidence, and field-level attribution. Security, provenance, and
compliance payloads are in
`cyclonedx-security-provenance-and-compliance.md`.

## BOM envelope and identity

The 1.6 rules in this section are attributed to `cyclonedx-1.6`.

### Reference-schema minimum

The draft-07 JSON root rejects extra keys and requires only `bomFormat` and
`specVersion`. `bomFormat` is fixed to `CycloneDX`, but `specVersion` is an
unconstrained string. A schema pass alone therefore does not prove that the
declared version matches the schema.

Validation of SPDX license identifiers and JSF signatures also needs the
sibling `spdx.schema.json` and `jsf-0.82.schema.json` schemas.

A recommended `serialNumber` is a lowercase `urn:uuid:` URI. Integer `version`
defaults to 1 and should increase whenever the same BOM is modified.

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
  "version": 2
}
```

### Media types and filenames

JSON and XML media types are `application/vnd.cyclonedx+json` and
`application/vnd.cyclonedx+xml`. Either may carry a `version=1.6` parameter.
Conventionally recognized filenames are `bom.json`, `bom.xml`, `*.cdx.json`,
and `*.cdx.xml`.

### BOM-Link

A whole BOM is `urn:cdx:<uuid>/<positive-version>`. Append `#<bom-ref>` for an
element:

```text
urn:cdx:3e671687-395b-41f5-a30f-a58921a69b79/2#component-a
```

Local `bom-ref` values should not begin with `urn:cdx:`. The schema validates
the lowercase URI shape but does not check referenced-object existence or
global `bom-ref` uniqueness.

### Extension properties

Root and object schemas generally reject arbitrary keys. Put custom data into
a supported `properties` array. Each entry requires `name`; `value` is
optional. Duplicate names are valid. Registration in the public CycloneDX
Property Taxonomy is encouraged for public names but is not required.

```json
{
  "properties": [
    {"name": "acme:reviewer", "value": "security"},
    {"name": "acme:reviewer", "value": "legal"}
  ]
}
```

## Metadata and component modeling

### Lifecycle metadata and preferred shapes

Every metadata lifecycle selects either:

- A predefined `phase`: `design`, `pre-build`, `build`, `post-build`,
  `operations`, `discovery`, or `decommission`.
- A custom `name` with optional description.

Use a metadata `tools` object containing component or service arrays instead of
the deprecated tool array. Replace:

| Deprecated form | Preferred form |
| --- | --- |
| `metadata.manufacture` | `metadata.component.manufacturer` |
| Component `author` | `authors` or `manufacturer` |
| Component `modified` | `pedigree` |
| Single-object identity evidence | Identity array |

```json
{
  "metadata": {
    "lifecycles": [{"phase": "build"}, {"name": "quality-gate"}],
    "tools": {
      "components": [{"type": "application", "name": "bom-generator"}]
    }
  }
}
```

### Data components

A component with type `data` should contain `data` entries. Each entry requires
type `source-code`, `configuration`, `dataset`, `definition`, or `other`.
Entries can embed or link content and record classification, sensitive data,
graphics, and governance.

```json
{
  "type": "data",
  "name": "training-set",
  "data": [{
    "type": "dataset",
    "classification": "confidential",
    "contents": {"url": "https://example.test/dataset"}
  }]
}
```

### Machine-learning model cards

A `machine-learning-model` should carry a model card covering parameters,
datasets, inputs and outputs, metrics, limitations, fairness, and environmental
consumption. Environmental measurement units are fixed to `kWh` and `tCO2eq`.

### External runtime components and ranges

The following behavior is attributed to `cyclonedx-1.7`.

Set `isExternal` only on runtime components supplied by the environment. It is
independent of `scope` and defaults to false. Never set it on
`metadata.component`.

Only an external component may use a Package URL `vers` string in
`versionRange`. `versionRange` and `version` are mutually exclusive.

```json
{
  "type": "library",
  "name": "runtime-api",
  "isExternal": true,
  "versionRange": "vers:npm/>=2.0.0|<3.0.0"
}
```

## Licensing

### Exclusive shape in 1.6

The 1.6 `licenses` field is one of:

- A list of `{ "license": ... }` objects. Each license contains either an SPDX
  `id` or a free-form `name`.
- Exactly one `{ "expression": ... }` object.

Do not mix these forms. Either may carry `declared` or `concluded`
acknowledgement. A license object may additionally capture licensor, licensee,
purchaser, purchase order, license types, renewal, and expiration.

```json
{
  "licenses": [{
    "expression": "Apache-2.0 AND (MIT OR GPL-2.0-only)",
    "acknowledgement": "concluded"
  }]
}
```

### Composable choices in 1.7

The 1.7 behavior here is attributed to `cyclonedx-1.7`.

The `licenses` array may mix `{license: ...}` and `{expression: ...}` entries
and may contain multiple expressions. Licenses and expressions may carry
`bom-ref`, commercial `licensing` data, and repeatable `properties`.

An expression may use `expressionDetails` to attach a `bom-ref`, text, or URL
to each constituent `licenseIdentifier`.

```json
{
  "licenses": [
    {"license": {"id": "Apache-2.0", "bom-ref": "lic-apache"}},
    {
      "expression": "MIT OR LicenseRef-Acme",
      "bom-ref": "lic-choice",
      "expressionDetails": [{
        "licenseIdentifier": "LicenseRef-Acme",
        "url": "https://example.test/license"
      }]
    }
  ]
}
```

## Dependencies and compositions

Every dependency entry requires `ref`. An explicit empty `dependsOn` says that
the object has no direct dependencies; omitting the object from the dependency
graph leaves its dependencies unknown. `provides` records implemented
specifications or components and does not imply that they are used.

Compositions separately express completeness with values such as `complete`,
`unknown`, and first- or third-party incomplete variants. Assembly and
dependency references are explicit and not transitive.

```json
{
  "dependencies": [
    {"ref": "app", "dependsOn": ["lib"]},
    {"ref": "lib", "dependsOn": []}
  ],
  "compositions": [{
    "aggregate": "incomplete_third_party_only",
    "dependencies": ["app"]
  }]
}
```

## Evidence and annotations

In 1.6, `evidence.identity` should be an array. Each identity requires a field
such as `purl` or `hash`. Analysis methods require `technique` and zero or one
`confidence`. Occurrences require `location`; call-stack frames require
`module`.

An annotation requires all of:

- `subjects`.
- Exactly one annotator kind: organization, individual, component, or service.
- A date-time `timestamp`.
- `text`.

Subjects may be local references or BOM-Link elements.

```json
{
  "evidence": {
    "identity": [{
      "field": "purl",
      "methods": [{
        "technique": "manifest-analysis",
        "confidence": 0.95
      }]
    }],
    "occurrences": [{"location": "package-lock.json"}]
  }
}
```

## Service data and governance

Every service `data` entry requires a classification and a flow relative to the
service: `inbound`, `outbound`, `bi-directional`, or `unknown`. Source and
destination entries are IRIs or BOM-Link element references.

Governance distinguishes custodians, stewards, and owners. Every responsible
party selects exactly one identity form: organization or individual contact.

```json
{
  "data": [{
    "flow": "outbound",
    "classification": "restricted",
    "destination": ["https://api.example.test/store"],
    "governance": {
      "owners": [{"organization": {"name": "Data Office"}}]
    }
  }]
}
```

## Field-level attribution

The citation behavior here is attributed to `cyclonedx-1.7`.

Top-level `citations` attribute BOM fields to a contributing entity or
formulation process. Every citation requires:

- `timestamp`.
- Exactly one of a nonempty `pointers` list or a nonempty `expressions` list.
- At least one of `attributedTo` or `process`.

Pointers are JSON Pointers in every serialization. Expressions use JSONPath
for JSON, XPath for XML, and JSONPath by default for Protocol Buffers.

```json
{
  "citations": [{
    "bom-ref": "citation-component-name",
    "pointers": ["/components/0/name"],
    "timestamp": "2025-10-21T12:00:00Z",
    "attributedTo": "tool-inventory"
  }]
}
```
