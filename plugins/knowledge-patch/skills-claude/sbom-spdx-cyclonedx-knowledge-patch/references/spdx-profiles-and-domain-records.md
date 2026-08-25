# SPDX profiles and domain records

Use this reference when choosing profile conformance points or authoring
profile-specific SPDX 3 records. Structural minima below do not replace OWL
and SHACL conformance checks.

## Profile conformance

The compositional rules here are attributed to
`spdx-3.0.1-specification`.

SPDX defines Core, Software, Security, Licensing, Dataset, AI, Build, Lite, and
Extension compliance points. Core is mandatory and is a prerequisite for every
other profile. The other points are optional, and support for one does not
imply support for another. The Licensing point has SimpleLicensing and
ExpandedLicensing forms, which express the same information differently.

The scope summary here is attributed to `spdx-3.0.1-model`:

- AI covers capabilities, use, limitations, training, data handling,
  explainability, and energy consumption.
- Build covers build-type URI, local identifier, entry point, configuration
  source and digest, parameters, times, and environment variables.
- Dataset covers collection, access, preparation, intended use, quality, and
  privacy.
- Security covers CVSS 2/3/4, EPSS, Exploit Catalog, SSVC, and VEX
  assessments.
- Software owns files, packages, SBOMs, snippets, and artifacts.
- Licensing consists of common Licensing data, text-formatted SimpleLicensing,
  and parseable machine-readable ExpandedLicensing.
- Information outside the defined profiles belongs in the separate
  `extension` namespace.

## Core record shapes and vocabularies

The schema-specific rules in the rest of this reference are attributed to
`spdx-3.0.1-json-schema`.

### Supporting-record structural minima

In addition to each object's class discriminator:

| Record | Required record-specific properties |
| --- | --- |
| `DictionaryEntry` | `key` |
| `ExternalIdentifier` | `externalIdentifierType`, `identifier` |
| `ExternalMap` | `externalSpdxId` |
| `NamespaceMap` | `namespace`, `prefix` |
| `Hash` | `algorithm`, `hashValue` |
| `PackageVerificationCode` | `algorithm`, `hashValue` |
| `ExternalRef` | None |

`Annotation` also needs inherited Element identity and creation data, plus
`annotationType` (`other` or `review`) and `subject`. The schema does not
require `statement`.

### Identifier and hash enums

`externalIdentifierType` permits:

```text
cpe22, cpe23, cve, email, gitoid, other, packageUrl, securityOther,
swhid, swid, urlScheme
```

Hash algorithms are:

```text
adler32, blake2b256, blake2b384, blake2b512, blake3,
crystalsDilithium, crystalsKyber, falcon, md2, md4, md5, md6, other,
sha1, sha224, sha256, sha384, sha3_224, sha3_256, sha3_384, sha3_512,
sha512
```

### External-reference types

When present, `externalRefType` is one of:

```text
altDownloadLocation, altWebPage, binaryArtifact, bower, buildMeta, buildSystem,
certificationReport, chat, componentAnalysisReport, cwe, documentation,
dynamicAnalysisReport, eolNotice, exportControlAssessment, funding, issueTracker,
license, mailingList, mavenCentral, metrics, npm, nuget, other, privacyAssessment,
productMetadata, purchaseOrder, qualityAssessmentReport, releaseHistory,
releaseNotes, riskAssessment, runtimeAnalysisReport, secureSoftwareAttestation,
securityAdversaryModel, securityAdvisory, securityFix, securityOther,
securityPenTestReport, securityPolicy, securityThreatModel, socialMedia,
sourceArtifact, staticAnalysisReport, support, vcs,
vulnerabilityDisclosureReport, vulnerabilityExploitabilityAssessment
```

`locator` is an array of unconstrained strings. `contentType` only verifies one
nonempty segment on each side of `/`.

### Profile and relationship enums

`profileConformance` is an array limited to:

```text
ai, build, core, dataset, expandedLicensing, extension, lite, security,
simpleLicensing, software
```

Relationship `completeness` is `complete`, `incomplete`, or `noAssertion`.
The complete `relationshipType` vocabulary is:

```text
affects, amendedBy, ancestorOf, availableFrom, configures, contains,
coordinatedBy, copiedTo, delegatedTo, dependsOn, descendantOf, describes,
doesNotAffect, expandsTo, exploitCreatedBy, fixedBy, fixedIn, foundBy,
generates, hasAddedFile, hasAssessmentFor, hasAssociatedVulnerability,
hasConcludedLicense, hasDataFile, hasDeclaredLicense, hasDeletedFile,
hasDependencyManifest, hasDistributionArtifact, hasDocumentation,
hasDynamicLink, hasEvidence, hasExample, hasHost, hasInput, hasMetadata,
hasOptionalComponent, hasOptionalDependency, hasOutput, hasPrerequisite,
hasProvidedDependency, hasRequirement, hasSpecification, hasStaticLink,
hasTest, hasTestCase, hasVariant, invokedBy, modifiedBy, other, packagedBy,
patchedBy, publishedBy, reportedBy, republishedBy, serializedInArtifact,
testedOn, trainedOn, underInvestigationFor, usesTool
```

## Software records

### Purpose, SBOM, and file enums

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

### Content identifiers and snippets

`software_ContentIdentifier` requires type `gitoid` or `swhid` and its value.
A `software_Snippet` requires `software_snippetFromFile`. Optional byte and line
ranges are `PositiveIntegerRange` objects whose endpoints are each at least
one. The schema does not ensure that the beginning precedes the end.

## Build profile

Beyond inherited Element fields, `build_Build` requires only
`build_buildType`. Build ID and times are scalar. Configuration-source digests,
entrypoints, URIs, environment entries, and parameters are arrays.

Digests are `Hash` records. Environment and parameter entries are
`DictionaryEntry` records, whose values may be absent.

```json
{
  "@context": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld",
  "type": "build_Build",
  "spdxId": "urn:spdx:build",
  "creationInfo": "urn:spdx:creation",
  "build_buildType": "https://example.test/build/type"
}
```

## AI profile

`ai_AIPackage` has no AI-specific required property. Autonomy and
sensitive-personal-information values are `yes`, `no`, or `noAssertion`.
Safety risk is `low`, `medium`, `high`, or `serious`.

Energy is split into optional training, fine-tuning, and inference arrays.
Each energy description requires a numeric or decimal-string quantity and a
unit of `kilowattHour`, `megajoule`, or `other`.

```json
{
  "ai_energyConsumption": {
    "type": "ai_EnergyConsumption",
    "ai_trainingEnergyConsumption": [{
      "type": "ai_EnergyConsumptionDescription",
      "ai_energyQuantity": 12.5,
      "ai_energyUnit": "kilowattHour"
    }]
  }
}
```

## Dataset profile

`dataset_DatasetPackage` requires a nonempty `dataset_datasetType` array chosen
from:

```text
audio, categorical, graph, image, noAssertion, numeric, other, sensor,
structured, syntactic, text, timeseries, timestamp, video
```

Size is a nonnegative integer. Availability is `clickthrough`,
`directDownload`, `query`, `registration`, or `scrapingScript`.
Confidentiality is `amber`, `clear`, `green`, or `red`.
Sensitive-personal-information is `yes`, `no`, or `noAssertion`.

## Security assessments and VEX

### Assessment-specific required fields

- CVSS 2 requires score and vector.
- CVSS 3 and 4 require score, severity, and vector.
- EPSS requires percentile and probability.
- Exploit Catalog requires catalog type, exploited flag, and locator.
- SSVC requires decision type.

CVSS 3/4 severity is `none`, `low`, `medium`, `high`, or `critical`.
Exploit Catalog type is `kev` or `other`. SSVC decision is `act`, `attend`,
`track`, or `trackStar`.

The schema does not bind an assessment subclass to its corresponding
`relationshipType`; enforce that association semantically.

### VEX subclass behavior

Affected VEX relationships require `security_actionStatement`. Fixed and
under-investigation subclasses add no status-specific required fields.
Not-affected relationships require neither an impact statement nor a
justification.

Optional not-affected justification values are:

```text
componentNotPresent, inlineMitigationsAlreadyExist,
vulnerableCodeCannotBeControlledByAdversary,
vulnerableCodeNotInExecutePath, vulnerableCodeNotPresent
```

## Licensing profiles

### SimpleLicensing

`simplelicensing_LicenseExpression` requires an unconstrained
`simplelicensing_licenseExpression` string. It may also have a semantic-version
`simplelicensing_licenseListVersion` and a
`simplelicensing_customIdToUri` array of dictionary mappings.

`simplelicensing_SimpleLicensingText` requires its license text. References can
also use `expandedlicensing_NoAssertionLicense` and
`expandedlicensing_NoneLicense`.

### ExpandedLicensing

Expanded conjunctive and disjunctive sets require at least two
`expandedlicensing_member` entries. An `expandedlicensing_OrLaterOperator`
requires its subject license. An `expandedlicensing_WithAdditionOperator`
requires both the addition and extendable-license subjects.

Custom and listed licenses require `simplelicensing_licenseText`. Custom and
listed additions require `expandedlicensing_additionText`. Member arrays do not
enforce uniqueness.
