# Schema Validation and Automation

Use these rules when validating SPDX or CycloneDX, interpreting schema
success, selecting exact enum spellings, or wiring validators into automation.

## Interpret the SPDX 2 JSON Schema (spdx-2.3-json-schema)

### Draft-07 schema closes modeled JSON objects

The official schema declares JSON Schema draft-07 with `$id`
`http://spdx.org/rdf/terms/2.3`. The root and every explicitly modeled nested
object set `additionalProperties` to `false`. Accepted properties therefore
must use their exact camel-case names, and arbitrary extension keys are
rejected. The unstructured objects in `artifactOfs` are the notable exception.

### The schema minimum is weaker than SPDX conformance

The only required root properties are `SPDXID`, `creationInfo`, `dataLicense`,
`name`, and `spdxVersion`. `creationInfo` in turn requires `created` and at
least one string in `creators`.

The schema does not require `documentNamespace` or any package, file, snippet,
or relationship array. Passing schema validation alone therefore does not
establish SPDX 2.3 conformance.

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

### Array members have their own required shapes

- A package requires `SPDXID`, `downloadLocation`, and `name`.
- A file requires `SPDXID`, `fileName`, and a nonempty `checksums` array whose
  objects contain `algorithm` and `checksumValue`.
- A snippet requires `SPDXID`, `snippetFromFile`, and nonempty `ranges`.
- A relationship requires `spdxElementId`, `relatedSpdxElement`, and
  `relationshipType`.

### Snippet ranges use reference-bearing pointer objects

Every snippet range requires both `startPointer` and `endPointer`. Each pointer
requires a `reference` to a file SPDX ID and may carry `offset`, `lineNumber`,
or both. The schema does not require either coordinate, so it accepts
reference-only pointers and leaves coordinate validity to semantic checks.

```json
{
  "SPDXID": "SPDXRef-Snippet",
  "snippetFromFile": "SPDXRef-File",
  "ranges": [{
    "startPointer": {
      "reference": "SPDXRef-File",
      "lineNumber": 10
    },
    "endPointer": {
      "reference": "SPDXRef-File",
      "lineNumber": 20
    }
  }]
}
```

### Nested records can be stricter than their containing arrays

Every annotation object requires `annotationDate`, `annotationType`,
`annotator`, and `comment`, even when the comment is empty.

Extracted license definitions live under the root property
`hasExtractedLicensingInfos`; each requires both `licenseId` and
`extractedText`. Each item in an optional `crossRefs` array requires `url`.

```json
{
  "hasExtractedLicensingInfos": [{
    "licenseId": "LicenseRef-Example",
    "extractedText": "Example license text"
  }]
}
```

### Package-purpose spelling differs in JSON

The JSON `primaryPackagePurpose` enum spells the operating-system value
`OPERATING_SYSTEM` with an underscore rather than the `OPERATING-SYSTEM`
spelling used by `tag:value`.

```json
{
  "primaryPackagePurpose": "OPERATING_SYSTEM"
}
```

### Lexical and cross-field constraints are not schema-validated

The schema supplies no `format`, `pattern`, `const`, union, or conditional
constraints. Consequently:

- identifiers, namespaces, version and data-license strings, dates, and
  digest text receive no lexical validation;
- references are not checked for existence; and
- cross-field requirements must be enforced outside the JSON Schema
  validator.

## Run local SPDX 3 validation (spdx-3.0.1-model)

### Local JSON-LD validation commands

For structural validation, `ajv-cli` requires a local schema and draft-2020
mode. `check-jsonschema` can instead consume the schema URL directly.

```shell
wget -O spdx-3-schema.json https://spdx.org/schema/3.0.1/spdx-json-schema.json
ajv validate --spec=draft2020 -s spdx-3-schema.json -d document.spdx3.json
check-jsonschema -v --schemafile https://spdx.org/schema/3.0.1/spdx-json-schema.json document.spdx3.json
```

Run the semantic pass with the SPDX model supplied as both the SHACL and
ontology graph:

```shell
pyshacl \
  --shacl https://spdx.org/rdf/3.0.1/spdx-model.ttl \
  --ont-graph https://spdx.org/rdf/3.0.1/spdx-model.ttl \
  document.spdx3.json
```

`pyshacl` warns about external SPDX IDs referenced through an `SpdxDocument`
import because it cannot interpret that import. Check those references
manually rather than treating the warnings as definitive failures.

## Interpret the SPDX 3 JSON Schema (spdx-3.0.1-json-schema)

### Structural validation permits semantically incomplete data

An empty `@graph` passes. `SpdxDocument` structurally adds no required
`dataLicense`, `element`, `rootElement`, `import`, or `namespaceMap`. The
element/root dependency and the semantically required package `name` are also
absent.

`CreationInfo.specVersion` accepts any semantic-version string rather than
requiring 3.0.1 or even 3.0.x.

### Timestamp and lexical validation quirks

All modeled timestamps must have whole-second
`YYYY-MM-DDThh:mm:ssZ` spelling, so offsets and fractional seconds are
rejected. The regex still admits impossible calendar and clock values such as
`2024-19-39T29:69:69Z`.

The `anyURI` definition is any string. An IRI merely needs nonempty text on
both sides of a colon and must not start `_:`. Hash values and CVSS vectors
are unchecked strings. CVSS/EPSS numbers accept a JSON number or decimal
string without range bounds.

### Core supporting-record minima

Beyond each object's class discriminator:

- `DictionaryEntry` requires only `key`;
- `ExternalIdentifier` requires `externalIdentifierType` and `identifier`;
- `ExternalMap` requires only `externalSpdxId`;
- `NamespaceMap` requires `namespace` and `prefix`; and
- `Hash` and `PackageVerificationCode` require `algorithm` and `hashValue`.

`ExternalRef` has no record-specific required properties. `Annotation`
additionally requires its Element identity and creation data plus
`annotationType` (`other` or `review`) and `subject`, but not `statement`.

### Identifier and hash vocabularies

The exact external-identifier types are:

```text
cpe22, cpe23, cve, email, gitoid, other, packageUrl, securityOther, swhid,
swid, urlScheme
```

Hash algorithms are:

```text
adler32, blake2b256, blake2b384, blake2b512, blake3,
crystalsDilithium, crystalsKyber, falcon, md2, md4, md5, md6, other,
sha1, sha224, sha256, sha384, sha3_224, sha3_256, sha3_384, sha3_512,
sha512
```

### External-reference vocabulary

When present, `externalRefType` is limited to the values below. `locator` is
an array of unconstrained strings; `contentType` only checks for one nonempty
segment on each side of `/`.

```text
altDownloadLocation, altWebPage, binaryArtifact, bower, buildMeta, buildSystem,
certificationReport, chat, componentAnalysisReport, cwe, documentation,
dynamicAnalysisReport, eolNotice, exportControlAssessment, funding, issueTracker,
license, mailingList, mavenCentral, metrics, npm, nuget, other, privacyAssessment,
productMetadata, purchaseOrder, qualityAssessmentReport, releaseHistory,
releaseNotes, riskAssessment, runtimeAnalysisReport, secureSoftwareAttestation,
securityAdversaryModel, securityAdvisory, securityFix, securityOther,
securityPenTestReport, securityPolicy, securityThreatModel, socialMedia,
sourceArtifact, staticAnalysisReport, support, vcs, vulnerabilityDisclosureReport,
vulnerabilityExploitabilityAssessment
```

### Relationship and profile enum spellings

`profileConformance` is an array limited to:

```text
ai, build, core, dataset, expandedLicensing, extension, lite, security,
simpleLicensing, software
```

Relationship `completeness` is `complete`, `incomplete`, or `noAssertion`.
The schema's complete `relationshipType` vocabulary is:

```text
affects, amendedBy, ancestorOf, availableFrom, configures, contains, coordinatedBy,
copiedTo, delegatedTo, dependsOn, descendantOf, describes, doesNotAffect, expandsTo,
exploitCreatedBy, fixedBy, fixedIn, foundBy, generates, hasAddedFile,
hasAssessmentFor, hasAssociatedVulnerability, hasConcludedLicense, hasDataFile,
hasDeclaredLicense, hasDeletedFile, hasDependencyManifest, hasDistributionArtifact,
hasDocumentation, hasDynamicLink, hasEvidence, hasExample, hasHost, hasInput,
hasMetadata, hasOptionalComponent, hasOptionalDependency, hasOutput, hasPrerequisite,
hasProvidedDependency, hasRequirement, hasSpecification, hasStaticLink, hasTest,
hasTestCase, hasVariant, invokedBy, modifiedBy, other, packagedBy, patchedBy,
publishedBy, reportedBy, republishedBy, serializedInArtifact, testedOn, trainedOn,
underInvestigationFor, usesTool
```

## Validate with `sbom-utility` (conformance-and-interoperability)

### `sbom-utility` selects versioned schemas from BOM metadata

`validate` detects a JSON BOM's declared format and version and uses the
matching embedded schema, including imported schemas. Supported CycloneDX and
SPDX 2.x documents can therefore be checked offline. The built-ins currently
reach CycloneDX 1.7 and SPDX 2.3. Inspect the exact versions and variants in a
binary with `schema list`.

```shell
sbom-utility schema list -q
sbom-utility validate -i bom.json
```

### `sbom-utility` has an automation-specific result contract

All commands return:

- `0` for success;
- `1` for an application error; or
- `2` for a validation failure.

Validation errors can be emitted as JSON. Only ten are formatted by default,
and `--error-value=false` omits potentially large failing values.

```shell
sbom-utility validate -i bom.json --format json \
  --error-limit 100 --error-value=false -q
```

### Alternate schemas and custom checks are separate mechanisms

`--force` validates with a schema at an `https://` or `file://` URI. A schema
registered through `--config-schema` can instead be selected by its
`--variant` name.

The experimental `--custom` path is different and CycloneDX-specific. Its
rule file currently supports `isUnique` and `hasProperties` checks.

```shell
sbom-utility validate -i bom.json --force file:///opt/schemas/bom.json
sbom-utility validate -i bom.json --config-schema config.json --variant corporate
sbom-utility validate -i bom.cdx.json --custom rules.json
```

## Check minimum elements (conformance-and-interoperability)

### Minimum-element checking covers SPDX 3 and CISA FSCT3

`ntia-conformance-checker` checks SPDX 2.2, 2.3, and 3.0 documents against
either the 2021 NTIA minimum elements or the 2024 CISA FSCT3 minimum
expectation. FSCT3 additionally requires license and copyright-holder
information.

Although SPDX 3 permits multiple SBOMs in one document, this checker currently
handles only one.

### `sbomcheck` defaults to SPDX 2 and NTIA

The package requires Python 3.10 or newer and validates input unless
`--skip-validation` is supplied. Select `spdx3` and `fsct3-min` explicitly
when needed. Reports can be `print`, `quiet`, `json`, or `html`.

```shell
pip install ntia-conformance-checker
sbomcheck -s spdx3 -c fsct3-min --output json \
  --output-file report.json bom.spdx3.json
```
