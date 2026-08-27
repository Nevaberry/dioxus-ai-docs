# SPDX serialization and validation

Use this reference for JSON, JSON-LD, RDF, canonicalization, and validation.
Schema acceptance is only the structural stage; apply the normative model and
cross-reference rules afterward.

## SPDX 2 JSON Schema

This section is attributed to `spdx-2.3-json-schema`.

### Dialect and closed objects

The official schema declares JSON Schema draft-07 and has `$id`
`http://spdx.org/rdf/terms/2.3`. The root and every explicitly modeled nested
object set `additionalProperties: false`. Properties therefore use exact
camel-case names, and arbitrary extension keys are rejected. The unstructured
objects in `artifactOfs` are the notable exception.

### Structural minimum versus conformance

The schema requires only these root properties:

```text
SPDXID, creationInfo, dataLicense, name, spdxVersion
```

`creationInfo` requires `created` and at least one string in `creators`. The
schema does not require `documentNamespace` or any package, file, snippet, or
relationship array. A schema-valid minimal object is therefore not necessarily
an SPDX-conformant document:

```json
{
  "SPDXID": "SPDXRef-DOCUMENT",
  "creationInfo": {
    "created": "2022-11-03T00:00:00Z",
    "creators": ["Tool: example-1.0"]
  },
  "dataLicense": "CC0-1.0",
  "name": "example",
  "spdxVersion": "SPDX-2.3"
}
```

### Required shapes within arrays

- A package requires `SPDXID`, `downloadLocation`, and `name`.
- A file requires `SPDXID`, `fileName`, and a nonempty `checksums` array.
  Every checksum requires `algorithm` and `checksumValue`.
- A snippet requires `SPDXID`, `snippetFromFile`, and nonempty `ranges`.
- A relationship requires `spdxElementId`, `relatedSpdxElement`, and
  `relationshipType`.

Each snippet range requires `startPointer` and `endPointer`. Each pointer
requires a `reference` to a file SPDX ID and may contain `offset`,
`lineNumber`, or both. Because the schema requires neither coordinate, it
accepts a reference-only pointer; enforce coordinate validity semantically.

```json
{
  "SPDXID": "SPDXRef-Snippet",
  "snippetFromFile": "SPDXRef-File",
  "ranges": [{
    "startPointer": {"reference": "SPDXRef-File", "lineNumber": 10},
    "endPointer": {"reference": "SPDXRef-File", "lineNumber": 20}
  }]
}
```

### Nested records

Every annotation object requires `annotationDate`, `annotationType`,
`annotator`, and `comment`, including an empty comment. Extracted license
definitions use the root property `hasExtractedLicensingInfos`. Each definition
requires `licenseId` and `extractedText`; if `crossRefs` is present, every item
requires `url`.

```json
{
  "hasExtractedLicensingInfos": [{
    "licenseId": "LicenseRef-Example",
    "extractedText": "Example license text"
  }]
}
```

### Serialization-specific enums and omission

JSON spells the operating-system `primaryPackagePurpose` value
`OPERATING_SYSTEM`, unlike the `OPERATING-SYSTEM` `tag:value` form.

For a file or snippet, omission of `licenseConcluded` or `copyrightText` means
`NOASSERTION`. Omission of file `licenseInfoInFiles` or snippet
`licenseInfoInSnippets` has the same meaning.

### Missing lexical and semantic checks

The schema uses no `format`, `pattern`, `const`, union, or conditional
constraints. It does not lexically validate identifiers, namespaces, version
and data-license strings, dates, or digest text. It does not check reference
existence or cross-field requirements. Add those checks outside the JSON
Schema validator.

## SPDX 3 serialization model

The RDF and canonicalization rules in this section are attributed to
`spdx-3.0.1-specification`.

### RDF serialization and document boundaries

The SPDX 3 model is RDF and may be serialized as JSON-LD, Turtle, N-Triples,
RDF/XML, or another RDF representation. A serialization defines at most one
`SpdxDocument`.

The serialized bytes are an `Artifact`, distinct from the logical document.
Connect the document to that artifact with a `serializedInArtifact`
relationship. Format-native information such as JSON-LD context prefixes may
stand in for the corresponding `namespaceMap`.

### Canonical SPDX

Canonical SPDX carries the same RDF data as the JSON-LD form but uses
deterministic, single-line JSON:

- No whitespace appears outside strings.
- Object names are unique ASCII strings sorted by name.
- Booleans and null use lowercase `true`, `false`, and `null`.
- Integers are base 10 without leading zeros.
- Quotes, backslashes, and control characters in UTF-8 strings are escaped.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld"}
```

### Context and two-stage validation

Every SPDX 3.0.1 JSON-LD document references this exact top-level context:

```text
https://spdx.org/rdf/3.0.1/spdx-context.jsonld
```

It aliases `spdxId` to `@id` and `type` to `@type`. Use both of these
validation artifacts:

```text
Schema:   https://spdx.org/schema/3.0.1/spdx-json-schema.json
Ontology: https://spdx.org/rdf/3.0.1/spdx-model.ttl
```

Conformance requires structural JSON Schema validation and semantic validation
against the OWL ontology, including its SHACL restrictions.

## SPDX 3 local validation

The commands and SHACL behavior in this section are attributed to
`spdx-3.0.1-model`.

Use draft-2020 mode when validating with `ajv-cli`. `check-jsonschema` can read
the schema URL directly:

```shell
wget -O spdx-3-schema.json https://spdx.org/schema/3.0.1/spdx-json-schema.json
ajv validate --spec=draft2020 -s spdx-3-schema.json -d document.spdx3.json
check-jsonschema -v \
  --schemafile https://spdx.org/schema/3.0.1/spdx-json-schema.json \
  document.spdx3.json
```

For the semantic pass, supply the SPDX model as both the SHACL and ontology
graph:

```shell
pyshacl \
  --shacl https://spdx.org/rdf/3.0.1/spdx-model.ttl \
  --ont-graph https://spdx.org/rdf/3.0.1/spdx-model.ttl \
  document.spdx3.json
```

`pyshacl` cannot interpret an `SpdxDocument` import. It consequently warns
about external SPDX IDs referenced through an import; check those references
manually rather than treating every such warning as a definitive failure.

## SPDX 3 JSON-LD schema envelope

The structural details in this section are attributed to
`spdx-3.0.1-json-schema`.

### Flat and graph forms

The root requires the exact global context. Alongside it, the schema accepts
either one recognized class or an `@graph` array of recognized class objects.
The root and known objects use `unevaluatedProperties: false`. The graph has no
minimum size.

```json
{
  "@context": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld",
  "@graph": [{
    "type": "CreationInfo",
    "created": "2024-12-17T00:00:00Z",
    "createdBy": ["urn:agent:builder"],
    "specVersion": "3.0.1"
  }]
}
```

### Identity, inline objects, and references

Every modeled class object needs its exact compact `type`. An `Element` also
requires an IRI-like `spdxId` and `creationInfo`. A non-Element record may
instead have an optional `@id`, either an IRI or a `_:` blank-node identifier.
Properties that target another class generally accept either a closed inline
object or an IRI/blank-node string reference.

```json
{
  "@context": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld",
  "type": "software_Package",
  "spdxId": "urn:spdx:pkg",
  "creationInfo": "urn:spdx:creation"
}
```

### Structurally accepted but semantically incomplete forms

The following pass structural validation:

- An empty `@graph`.
- An `SpdxDocument` without `dataLicense`, `element`, `rootElement`, `import`,
  or `namespaceMap`.
- A populated collection without the normative element/root dependency.
- A package without its semantically required `name`.
- `CreationInfo.specVersion` containing any semantic-version string, rather
  than specifically 3.0.1 or even 3.0.x.

Reject or repair these in the semantic pass as appropriate.

### Extension payloads

Known SPDX objects are closed. An item in an Element's `extension` array may,
however, use an IRI as `type` and carry arbitrary properties:

```json
{
  "@context": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld",
  "type": "software_Package",
  "spdxId": "urn:spdx:pkg",
  "creationInfo": "urn:spdx:creation",
  "extension": [{
    "type": "https://example.test/spdx#Review",
    "reviewer": "security"
  }]
}
```

The dedicated `extension_CdxPropertiesExtension` definition requires a
nonempty `extension_cdxProperty` array, and each entry requires
`extension_cdxPropName`. The generic extension alternative can nevertheless
accept the same type without that dedicated payload, so enforce the intended
shape semantically.

### Timestamp and lexical quirks

Modeled timestamps require whole-second `YYYY-MM-DDThh:mm:ssZ`; offsets and
fractional seconds fail. The regex nevertheless accepts impossible dates and
times such as `2024-19-39T29:69:69Z`, so perform a real calendar check.

`anyURI` accepts any string. An IRI only needs nonempty text on both sides of a
colon and must not start `_:`. Hash values and CVSS vectors are unchecked
strings. CVSS and EPSS numbers accept a JSON number or decimal string without
range bounds. Validate all of these semantically.
