# SPDX document and package authoring

Use this reference while constructing document graphs, packages, files,
relationships, and Lite records. Serialization and validation details are in
`spdx-serialization-and-validation.md`; profile-specific record shapes are in
`spdx-profiles-and-domain-records.md`.

## SPDX 2 document structure

The following rules are attributed to `spdx-2.3-core`.

### Supported serializations and losslessness

SPDX 2.3 supports YAML 1.2, JSON, RDF/XML, `tag:value`, and `.xls`. Generic XML
is still described as a future format even though `.spdx.xml` appears in the
suggested filename table. Do not infer generic XML support from that filename.
Supported representations must translate without information loss. Tags and
format properties are case-sensitive.

An implementation may conform to the defined SPDX Lite subset rather than the
entire specification.

### `tag:value` ordering carries structure

Packages and files are independently optional. A file need not belong to a
package, but `tag:value` ordering establishes containment:

- Standalone files precede every package.
- Files contained by a package immediately follow that package.
- A new package ends the preceding package's file set unless an explicit
  relationship states otherwise.
- A file begins with its file-name field.
- Snippets immediately follow their associated file.
- A new file or package ends the preceding snippet set.

RDF does not rely on this ordering; it uses `spdx:hasFile` to associate files
with packages explicitly.

### Reviews are annotations

The legacy review-information section is retained only for SPDX 1.2
compatibility and has been deprecated since SPDX 2.0. Record new reviews as
annotations with type `REVIEW`. A legacy review requires a review date, and
adding it must not modify the document's original `Created` timestamp.

### Revision and external-document identity

`DocumentNamespace` is a unique absolute URI. It must have a scheme, must not
contain a `#` fragment, and need not resolve. Assign a different URI to every
updated revision:

```text
DocumentNamespace: https://example.com/spdx/example-2.3-550e8400-e29b-41d4-a716-446655440000
```

Each external document reference contains:

1. A locally unique identifier beginning `DocumentRef-`; the suffix permits
   letters, digits, `.`, `-`, and `+`.
2. The referenced document's namespace URI.
3. A checksum of the referenced document.

```text
ExternalDocumentRef: DocumentRef-upstream https://example.com/spdx/upstream-1 SHA1: d6a770ba38583ed4bb4525bd96e50461655d2759
```

## SPDX 2 packages and relationships

The following rules are attributed to `spdx-2.3-package-model`.

### `FilesAnalyzed` controls legal fields

`FilesAnalyzed` is optional and defaults to `true`. When false, the package
represents metadata or a URI reference, must contain no files, and must omit
`PackageVerificationCode` and `PackageLicenseInfoFromFiles`. Relationships may
still connect it to analyzed elements.

```text
PackageName: external-lib
SPDXID: SPDXRef-external-lib
FilesAnalyzed: false
Relationship: SPDXRef-app STATIC_LINK SPDXRef-external-lib
```

### Verification code versus artifact checksum

For an analyzed package, compute `PackageVerificationCode` as follows:

1. SHA-1 hash every non-excluded file.
2. Normalize the digests to lowercase.
3. Sort the digests in ASCII order.
4. Concatenate them without separators.
5. SHA-1 hash the concatenated string.

Embedded SPDX analysis files may be named as exclusions.
`PackageChecksum`, by contrast, hashes the package artifact itself. It should
not be calculated when the SPDX document will be embedded into that artifact.
Recognized algorithms added in SPDX 2.3 include SHA3-256/384/512,
BLAKE2b-256/384/512, BLAKE3, and ADLER32.

```text
PackageVerificationCode: d6a770ba38583ed4bb4525bd96e50461655d2758 (excludes: ./package.spdx)
PackageChecksum: BLAKE3: 11b6d3ee554eedf79299905a98f9b9a04e498210b59f15094c916c91d150efcd
```

### License and copyright omission semantics

Omission of `PackageLicenseConcluded`, `PackageLicenseDeclared`, or
`PackageCopyrightText` means `NOASSERTION`. When `FilesAnalyzed` is true or
absent, omission of `PackageLicenseInfoFromFiles` also means `NOASSERTION`.
When `FilesAnalyzed` is false, that field must instead be absent. `NONE`
remains an explicit assertion that no applicable license or copyright
information exists.

### Purpose and lifecycle timestamps

`PrimaryPackagePurpose` is an optional scalar. The original publication's
`0..*` cardinality was an error; use `0..1`. Tag values are:

```text
APPLICATION, FRAMEWORK, LIBRARY, CONTAINER, OPERATING-SYSTEM, DEVICE,
FIRMWARE, SOURCE, ARCHIVE, FILE, INSTALL, OTHER
```

`ReleaseDate`, `BuiltDate`, and `ValidUntilDate` respectively mean release
time, actual build time, and supplier support-end time. Each occurs at most
once and uses `YYYY-MM-DDThh:mm:ssZ` UTC form.

```text
PrimaryPackagePurpose: CONTAINER
ReleaseDate: 2022-10-01T12:00:00Z
BuiltDate: 2022-09-30T18:30:22Z
ValidUntilDate: 2025-10-01T00:00:00Z
```

### External references

Each repeatable `ExternalRef` is `<category> <type> <locator>`, and the locator
contains no spaces. Categories are `SECURITY`, `PACKAGE-MANAGER`,
`PERSISTENT-ID`, and `OTHER`. SPDX 2.3 expands security types to advisories,
fixes, generic URLs, and SWID data, and persistent identifiers to gitoids.
Advisory references are creation-time snapshots; consumers should expect them
to become stale.

```text
ExternalRef: SECURITY advisory https://example.com/security/CVE-2022-0001
ExternalRef: SECURITY fix https://example.com/commits/0123456789abcdef
ExternalRef: PERSISTENT-ID gitbom gitoid:blob:sha1:d8bcd58df2b14818b8237bb70c979d62c7df5747
```

### Relationship completeness

Relationships are generally optional. `DESCRIBES` is mandatory when a document
contains more than one package or a set of standalone files. The right-hand
target communicates completeness:

- `NONE` asserts there are no related elements.
- `NOASSERTION` says the relationship is unknown.
- Omission, or listing only some relationships, makes no completeness claim.

SPDX 2.3 adds `REQUIREMENT_DESCRIPTION_FOR` and `SPECIFICATION_FOR`. In
`tag:value`, a `RelationshipComment` applies only to the immediately preceding
relationship and must immediately follow it.

```text
Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-product
Relationship: SPDXRef-requirements REQUIREMENT_DESCRIPTION_FOR SPDXRef-product
RelationshipComment: <text>Defines the product's license-policy requirement.</text>
Relationship: SPDXRef-product DEPENDS_ON NOASSERTION
```

### NTIA minimum-element mapping

SPDX Lite incorporates the NTIA minimum SBOM elements. Map:

| NTIA concept | SPDX 2 field or structure |
| --- | --- |
| Author | `Creator` |
| Supplier, name, version, hash | `PackageSupplier`, `PackageName`, `PackageVersion`, `PackageChecksum` |
| Unique identity | Package SPDX identifier plus `DocumentNamespace` |
| Component inclusion | `CONTAINS` or `DESCRIBES`; the document describes at least one package |
| Timestamp | `Created` |

## SPDX 3 collections, packages, and relationships

The collection and package guidance in this section is attributed to
`spdx-3.0.1-model`.

### Collections and roots

`ElementCollection` is an abstract Core `Element`. It conforms to Core even
when `profileConformance` is omitted, because `core` is the default. An empty
collection may omit roots. Once `element` contains any member, `rootElement`
must also contain a member. Neither property may contain an `SpdxDocument`.

### Relationships are Elements

`Relationship` is a concrete `Element` with exactly one `from`, exactly one
`relationshipType`, one or more `to` values, and optional scalar
`completeness`, `startTime`, and `endTime`. Represent explicit absence with
`NoneElement` as the sole target; mixing it with other targets is invalid.
`NoAssertionElement` represents an intentional lack of an assertion.

### Package artifact granularity

`Package` subclasses `/Software/SoftwareArtifact`. It adds optional scalar
`downloadLocation`, `homePage`, `packageVersion`, `packageUrl`, and
`sourceInfo`, and strengthens inherited `name` to at least one value.

A package may represent an archive, directory, language package or module,
container image or individual layer, collection of subpackages, or repository
snapshot. Depending on the intended granularity, some of those artifacts may
instead be modeled as files.

### Compact names and arrays

Core JSON-LD class and property names keep their original names. Non-Core names
prefix the original case with the lowercase profile and `_`, for example:

```text
dataset_datasetType
expandedlicensing_CustomLicense
Person
```

Any property whose maximum cardinality exceeds one must be an array even when
only one value is serialized.

## SPDX Lite graph construction

The requirements in this section are attributed to
`spdx-3.0.1-specification`.

### Document and SBOM roots

A Lite `SpdxDocument` requires `creationInfo`, `spdxId`, `element`, and
`rootElement`. Its `element` array must include an SBOM object, and SBOM objects
should be its roots. Document `dataLicense` and `name` are recommended, not
mandatory.

A Lite `/Software/Sbom` requires the same four fields. Its `element` must
include at least one `/Software/Package`, and package objects are the preferred
roots.

### Package and license minimums

A Lite `/Software/Package` requires `copyrightText`, `creationInfo`, `name`,
`packageVersion`, `spdxId`, and `suppliedBy`, preferably pointing to a
`/Core/Agent`. It also needs at least one of `downloadLocation` or `packageUrl`.

Exactly one `hasConcludedLicense` and one `hasDeclaredLicense` relationship
must originate from every package. Each targets
`/SimpleLicensing/AnyLicenseInfo`.

### Supporting Lite records

- `CreationInfo` requires `created`, one or more `createdBy` agents, and
  `specVersion` fixed to `3.0.*` for a supported patch release.
- An Agent requires `creationInfo`, `name`, and `spdxId`.
- A Hash requires `algorithm` and `hashValue`.
- A license expression requires `creationInfo`, `spdxId`, and
  `licenseExpression`.
- Simple licensing text requires `creationInfo`, `spdxId`, and `licenseText`.
- A Relationship requires `creationInfo`, `from`, `relationshipType`,
  `spdxId`, and one or more `to` values.
