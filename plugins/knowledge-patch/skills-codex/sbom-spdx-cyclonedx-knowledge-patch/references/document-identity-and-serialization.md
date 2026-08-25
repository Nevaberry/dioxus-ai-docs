# Document Identity and Serialization

Use these rules when choosing a wire format, assigning a document identity,
linking documents, or adding extension data.

## Establish SPDX 2 document identity (spdx-2.3-core)

### Document namespaces identify immutable revisions

`DocumentNamespace` must be a unique absolute URI with a scheme and no `#`
fragment. Each updated version of a document needs a new URI; the URI does not
need to resolve.

```text
DocumentNamespace: https://example.com/spdx/example-2.3-550e8400-e29b-41d4-a716-446655440000
```

### External document references are checksum-bound

Each optional external reference combines a locally unique `DocumentRef-`
identifier, the referenced document's namespace URI, and a checksum. The
identifier suffix may contain letters, digits, `.`, `-`, and `+`.

```text
ExternalDocumentRef: DocumentRef-upstream https://example.com/spdx/upstream-1 SHA1: d6a770ba38583ed4bb4525bd96e50461655d2759
```

## Choose an SPDX 2 serialization (spdx-2.3-core)

### Serialization support and XML status

SPDX 2.3 supports YAML 1.2, JSON, RDF/XML, `tag:value`, and `.xls`. Generic XML
is still described as in development for a later release, despite `.spdx.xml`
appearing in the suggested filename table. Supported formats must translate
without loss, and tags and format properties are case-sensitive.

### Structure encoded by `tag:value` ordering

Packages and files are independently optional, so a file need not be wrapped
by a package. In `tag:value`, however:

- contained files must immediately follow their package;
- standalone files must precede all packages;
- a new package ends the preceding package's file set unless an explicit
  relationship says otherwise;
- a file starts with its file-name field;
- snippets follow their associated file; and
- a new file or package ends the snippet set.

RDF instead associates package files explicitly with `spdx:hasFile`.

## Identify and serialize CycloneDX BOMs (cyclonedx-1.6)

### Reference-schema minimum and BOM identity

The draft-07 root rejects extra keys and requires only `bomFormat` and
`specVersion`. `bomFormat` is fixed to `CycloneDX`, but `specVersion` is an
unconstrained string. Validating SPDX license IDs or JSF signatures also
requires the sibling `spdx.schema.json` or `jsf-0.82.schema.json`.

A recommended `serialNumber` must be a lowercase `urn:uuid:` value. Integer
`version` defaults to 1 and should increase whenever that same BOM is modified.

```json
{"bomFormat":"CycloneDX","specVersion":"1.6","serialNumber":"urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79","version":2}
```

### Media-type versioning and recognized filenames

JSON and XML use `application/vnd.cyclonedx+json` and
`application/vnd.cyclonedx+xml`. Either may carry a `version=1.6` parameter.
Conventionally recognized names are `bom.json`, `bom.xml`, `*.cdx.json`, and
`*.cdx.xml`.

### BOM-Link cross-document references

A whole BOM is addressed as `urn:cdx:<uuid>/<positive-version>`, while an
element adds `#<bom-ref>`. Local `bom-ref` values should not start with
`urn:cdx:`. The schema validates the lowercase URI shape but does not enforce
reference existence or global `bom-ref` uniqueness.

```text
urn:cdx:3e671687-395b-41f5-a30f-a58921a69b79/2#component-a
```

## Serialize the SPDX 3 RDF model (spdx-3.0.1-specification)

### RDF serializations and document boundaries

The SPDX 3 model is RDF, so it can be serialized as JSON-LD, Turtle,
N-Triples, RDF/XML, or another RDF format. One serialization may define at
most one `SpdxDocument`. Its bytes are modeled as an `Artifact` linked from
the logical document by a `serializedInArtifact` relationship. Format-native
data such as JSON-LD context prefixes may stand in for the corresponding
`namespaceMap`.

### Canonical serialization

Canonical SPDX contains the same RDF data as its JSON-LD form but uses
deterministic, single-line JSON with no whitespace outside strings:

- object names are unique ASCII strings ordered by name;
- literals use lowercase `true`, `false`, and `null`;
- integers are base-10 without leading zeros; and
- quotes, backslashes, and control characters in UTF-8 strings are escaped.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld"}
```

### JSON-LD context and two-stage validation

Every SPDX 3.0.1 JSON-LD document must reference the global context below at
the top level. The context aliases `spdxId` to `@id` and `type` to `@type`.
Conformance requires structural validation against the JSON Schema and
semantic validation against the OWL ontology, including its SHACL
restrictions; a schema-only pass is insufficient.

```text
Context:  https://spdx.org/rdf/3.0.1/spdx-context.jsonld
Schema:   https://spdx.org/schema/3.0.1/spdx-json-schema.json
Ontology: https://spdx.org/rdf/3.0.1/spdx-model.ttl
```

## Encode SPDX 3 JSON-LD objects (spdx-3.0.1-json-schema)

### Flat and graph JSON-LD envelopes

The schema requires the exact string context and accepts either one recognized
class beside it or an `@graph` array of recognized class objects. The root and
known object forms use `unevaluatedProperties: false`; `@graph` has no minimum
size.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld","@graph":[{"type":"CreationInfo","created":"2024-12-17T00:00:00Z","createdBy":["urn:agent:builder"],"specVersion":"3.0.1"}]}
```

### Object identity and reference encoding

Every schema-modeled class object needs its exact compact `type`. An `Element`
also needs an IRI-like `spdxId` and `creationInfo`, while non-element records
may instead have an optional `@id` that can be an IRI or `_:` blank-node
identifier. Properties targeting another class generally accept either a
closed inline object or an IRI/blank-node string reference.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld","type":"software_Package","spdxId":"urn:spdx:pkg","creationInfo":"urn:spdx:creation"}
```

## Preserve compact names and cardinality (spdx-3.0.1-model)

### Serialized names and collection cardinality

Non-Core JSON-LD names use the lowercase profile name followed by `_` and the
original class or property case; Core names omit the prefix. Any property
whose cardinality can exceed one must be an array even when it currently has
only one value.

```text
dataset_datasetType
expandedlicensing_CustomLicense
Person
```

## Add extension data

### Extension data uses repeatable properties (cyclonedx-1.6)

Because arbitrary root and object keys are generally rejected, custom data
belongs in supported `properties` arrays. Each entry requires `name`; `value`
is optional. Duplicate names are valid. Registering public names in the
CycloneDX Property Taxonomy is encouraged but optional.

```json
{"properties":[{"name":"acme:reviewer","value":"security"},{"name":"acme:reviewer","value":"legal"}]}
```

### Open extension payloads (spdx-3.0.1-json-schema)

Known SPDX objects are closed, but an item in an Element's `extension` array
may use an IRI as its `type` and carry arbitrary properties. The dedicated
`extension_CdxPropertiesExtension` definition requires a nonempty
`extension_cdxProperty` array whose entries require
`extension_cdxPropName`. The generic extension alternative can still accept
that type without the dedicated payload, so enforce the intended shape
semantically.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld","type":"software_Package","spdxId":"urn:spdx:pkg","creationInfo":"urn:spdx:creation","extension":[{"type":"https://example.test/spdx#Review","reviewer":"security"}]}
```
