# Components, Dependencies, and Provenance

Use these rules when modeling packages, files, snippets, components, services,
relationships, evidence, lifecycle data, and build provenance.

## Author SPDX 2 packages (spdx-2.3-package-model)

### `FilesAnalyzed` controls which package fields are legal

`FilesAnalyzed` is optional and defaults to `true`. When it is `false`, the
package represents metadata or a URI reference and must contain no files. Such
a package must also omit `PackageVerificationCode` and
`PackageLicenseInfoFromFiles`, but relationships can connect it to analyzed
elements.

```text
PackageName: external-lib
SPDXID: SPDXRef-external-lib
FilesAnalyzed: false
Relationship: SPDXRef-app STATIC_LINK SPDXRef-external-lib
```

### Package verification codes differ from package checksums

For an analyzed package, compute `PackageVerificationCode` by:

1. SHA-1 hashing every non-excluded file;
2. sorting the lowercase digests in ASCII order;
3. concatenating them without separators; and
4. SHA-1 hashing that string.

Embedded SPDX analysis files can be named as exclusions. `PackageChecksum`
instead hashes the package artifact and should not be calculated when the SPDX
document will be embedded. SPDX 2.3 recognizes SHA3-256/384/512,
BLAKE2b-256/384/512, BLAKE3, and ADLER32 in addition to earlier algorithms.

```text
PackageVerificationCode: d6a770ba38583ed4bb4525bd96e50461655d2758 (excludes: ./package.spdx)
PackageChecksum: BLAKE3: 11b6d3ee554eedf79299905a98f9b9a04e498210b59f15094c916c91d150efcd
```

### SPDX 2.3 adds package purpose and lifecycle dates

`PrimaryPackagePurpose` is a single optional value:

```text
APPLICATION, FRAMEWORK, LIBRARY, CONTAINER, OPERATING-SYSTEM, DEVICE,
FIRMWARE, SOURCE, ARCHIVE, FILE, INSTALL, OTHER
```

The original 2.3 publication's `0..*` cardinality was an error; the correct
cardinality is `0..1`. `ReleaseDate`, `BuiltDate`, and `ValidUntilDate`
respectively record release time, actual build time, and the supplier's
support-end time. Each occurs at most once and uses
`YYYY-MM-DDThh:mm:ssZ` UTC form.

```text
PrimaryPackagePurpose: CONTAINER
ReleaseDate: 2022-10-01T12:00:00Z
BuiltDate: 2022-09-30T18:30:22Z
ValidUntilDate: 2025-10-01T00:00:00Z
```

### External references carry security and persistent identifiers

Each repeatable `ExternalRef` is `<category> <type> <locator>`. The category is
`SECURITY`, `PACKAGE-MANAGER`, `PERSISTENT-ID`, or `OTHER`; the locator
contains no spaces. SPDX 2.3 expands security references to advisories, fixes,
generic URLs, and SWID data, and persistent references to gitoids. Enumerated
advisories are a creation-time snapshot, so consumers should assume they
become stale.

```text
ExternalRef: SECURITY advisory https://example.com/security/CVE-2022-0001
ExternalRef: SECURITY fix https://example.com/commits/0123456789abcdef
ExternalRef: PERSISTENT-ID gitbom gitoid:blob:sha1:d8bcd58df2b14818b8237bb70c979d62c7df5747
```

## Express SPDX 2 relationships (spdx-2.3-package-model)

### Relationships can express incomplete knowledge

Relationships are optional except that `DESCRIBES` is mandatory when a
document contains more than one package or a set of standalone files.

- A right-hand `NONE` asserts no related elements.
- `NOASSERTION` leaves the relationship unknown.
- Omitting relationships or listing only some makes no completeness claim.
- SPDX 2.3 adds `REQUIREMENT_DESCRIPTION_FOR` and `SPECIFICATION_FOR`.
- In `tag:value`, a `RelationshipComment` applies only to and must immediately
  follow its relationship.

```text
Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-product
Relationship: SPDXRef-requirements REQUIREMENT_DESCRIPTION_FOR SPDXRef-product
RelationshipComment: <text>Defines the product's license-policy requirement.</text>
Relationship: SPDXRef-product DEPENDS_ON NOASSERTION
```

## Record reviews as annotations (spdx-2.3-core)

### Reviews belong in annotations

The review-information section is retained only for SPDX 1.2 compatibility
and has been deprecated since SPDX 2.0. New review information uses an
annotation whose type is `REVIEW`. Adding a legacy review requires its review
date and must not change the document's original `Created` timestamp.

## Build SPDX 3 collections and relationships (spdx-3.0.1-model)

### `ElementCollection` is abstract and root-constrained

`ElementCollection` is an abstract Core `Element`. It conforms to Core even
when `profileConformance` is absent, in which case `core` is the default. An
empty collection may omit roots, but once `element` has a member,
`rootElement` must also have a member. Neither property may contain an
`SpdxDocument`.

### SPDX 3 relationships are elements

`Relationship` is a concrete `Element` with exactly one `from` and
`relationshipType`, one or more `to` values, and optional single
`completeness`, `startTime`, and `endTime` values.

Explicit absence is represented by making `NoneElement` the sole `to` value;
mixing it with other targets is invalid. `NoAssertionElement` represents an
intentional lack of an assertion.

### The base package shape does not prescribe artifact granularity

`Package` subclasses `/Software/SoftwareArtifact`, adds optional single
`downloadLocation`, `homePage`, `packageVersion`, `packageUrl`, and
`sourceInfo` values, and strengthens the inherited `name` property to at least
one value.

A package may represent an archive, directory, language package or module,
container image or individual layer, collection of subpackages, or repository
snapshot. Those artifacts may sometimes be modeled as files instead.

## Author SPDX software objects (spdx-3.0.1-json-schema)

### Software purpose, SBOM, and file enums

`software_primaryPurpose` is scalar and `software_additionalPurpose` is an
array. Both use:

```text
application, archive, bom, configuration, container, data, device,
deviceDriver, diskImage, documentation, evidence, executable, file,
filesystemImage, firmware, framework, install, library, manifest, model,
module, operatingSystem, other, patch, platform, requirement, source,
specification, test
```

`software_Sbom.software_sbomType` is an optional array of `analyzed`, `build`,
`deployed`, `design`, `runtime`, or `source`.
`software_File.software_fileKind` is optionally `directory` or `file`.

### Content identifiers and snippet ranges

`software_ContentIdentifier` requires a `gitoid` or `swhid` type plus its
value. A `software_Snippet` requires `software_snippetFromFile`. Byte and line
ranges are optional `PositiveIntegerRange` objects whose endpoints must each
be at least 1, but the schema does not require the beginning to precede the
end.

## Model CycloneDX dependency completeness (cyclonedx-1.6)

### Dependency graphs distinguish empty from unknown

Every dependency entry requires `ref`. An explicit empty `dependsOn` means
the object has no direct dependencies; omitting the object from the graph
leaves its dependencies unknown. `provides` records implemented
specifications or components without implying use.

Compositions separately qualify completeness with values such as `complete`,
`unknown`, or the first-/third-party incomplete variants. Assembly and
dependency references are explicit rather than transitive.

```json
{"dependencies":[{"ref":"app","dependsOn":["lib"]},{"ref":"lib","dependsOn":[]}],"compositions":[{"aggregate":"incomplete_third_party_only","dependencies":["app"]}]}
```

## Add CycloneDX lifecycle and evidence (cyclonedx-1.6)

### Lifecycle metadata and preferred 1.6 forms

Each metadata lifecycle is either a predefined `phase`—`design`, `pre-build`,
`build`, `post-build`, `operations`, `discovery`, or `decommission`—or a
custom `name` with optional description.

Metadata tools should use an object containing component/service arrays
rather than the deprecated tool array. Also replace:

- `metadata.manufacture` with `metadata.component.manufacturer`;
- component `author` with `authors` or `manufacturer`;
- component `modified` with `pedigree`; and
- single-object identity evidence with the 1.6 array form.

```json
{"metadata":{"lifecycles":[{"phase":"build"},{"name":"quality-gate"}],"tools":{"components":[{"type":"application","name":"bom-generator"}]}}}
```

### Component evidence and annotations have strict inner shapes

In 1.6, `evidence.identity` should be an array. Each identity requires a field
such as `purl` or `hash`; analysis methods require `technique` and 0–1
`confidence`; occurrences require `location`; and call-stack frames require
`module`.

An annotation requires `subjects`, exactly one annotator kind—organization,
individual, component, or service—a date-time `timestamp`, and `text`.
Subjects may be local references or BOM-Link elements.

```json
{"evidence":{"identity":[{"field":"purl","methods":[{"technique":"manifest-analysis","confidence":0.95}]}],"occurrences":[{"location":"package-lock.json"}]}}
```

## Capture executable provenance (cyclonedx-1.6)

### Formulation captures executable build and deployment provenance

Top-level `formulation` holds formulas with transient components/services and
independently triggered workflows. Every workflow and task requires
`bom-ref`, deployment-context `uid`, and a `taskTypes` array whose values
include `build`, `scan`, `test`, `deliver`, or `deploy`.

The model can also preserve task dependency and runtime-topology graphs,
triggers and conditions, ordered command steps, typed inputs/outputs, and
shareable workspaces and volumes.

```json
{"formulation":[{"workflows":[{"bom-ref":"workflow-build","uid":"run-42","taskTypes":["build"],"tasks":[{"bom-ref":"task-build","uid":"build-42","taskTypes":["build"],"steps":[{"commands":[{"executed":"npm ci"}]}]}]}]}]}
```

## Model external runtime components (cyclonedx-1.7)

### External runtime components and version ranges

Set `isExternal` only for runtime components supplied by the environment,
never for `metadata.component`. This is independent of `scope` and defaults
to `false`. Only an external component may use a Package URL `vers` value in
`versionRange`; `versionRange` and `version` are mutually exclusive.

```json
{"type":"library","name":"runtime-api","isExternal":true,"versionRange":"vers:npm/>=2.0.0|<3.0.0"}
```

## Attribute individual fields (cyclonedx-1.7)

### Field-level data attribution

Top-level `citations` attribute BOM fields to a contributing entity or
formulation process. Every citation requires:

- `timestamp`;
- exactly one of nonempty `pointers` or `expressions`; and
- at least one of `attributedTo` or `process`.

Pointers are always JSON Pointers across serializations. Expressions use
JSONPath for JSON, XPath for XML, and JSONPath by default for Protocol
Buffers.

```json
{"citations":[{
  "bom-ref":"citation-component-name",
  "pointers":["/components/0/name"],
  "timestamp":"2025-10-21T12:00:00Z",
  "attributedTo":"tool-inventory"
}]}
```
