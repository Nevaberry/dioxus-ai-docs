# Profiles, Standards, and Specialized Data

Use these rules when claiming profile conformance, meeting minimum-element
policies, or modeling AI, datasets, services, standards, declarations,
distribution controls, and patents.

## Claim SPDX 2 Lite conformance (spdx-2.3-core)

### SPDX Lite conformance

An implementation may conform to the SPDX Lite profile, a defined subset,
instead of conforming to the entire SPDX specification.

## Map minimum SBOM elements into SPDX 2 (spdx-2.3-package-model)

### NTIA minimum elements have a direct SPDX mapping

SPDX 2.3 updates SPDX Lite to require the NTIA SBOM minimum fields. Map them
as follows:

| Minimum element | SPDX representation |
| --- | --- |
| Author | `Creator` |
| Supplier | `PackageSupplier` |
| Component name | `PackageName` |
| Component version | `PackageVersion` |
| Component hash | `PackageChecksum` |
| Unique identity | Package SPDX identifier plus `DocumentNamespace` |
| Component inclusion | `CONTAINS` or `DESCRIBES` |
| Timestamp | `Created` |

The document must describe at least one package.

## Select SPDX 3 profiles (spdx-3.0.1-specification)

### Profile conformance is compositional

SPDX 3.0.1 defines Core, Software, Security, Licensing, Dataset, AI, Build,
Lite, and Extension compliance points. Core is mandatory and is a prerequisite
for every other profile. The others are optional, and support for one does not
imply support for another.

The Licensing compliance point has SimpleLicensing and ExpandedLicensing forms
that express the same information differently.

## Understand profile scope (spdx-3.0.1-model)

### Profile scopes

- AI covers capabilities, use, limitations, training, data handling,
  explainability, and energy consumption.
- Build records the build type URI, local identifier, entry point,
  configuration source and digest, parameters, times, and environment
  variables.
- Dataset covers collection, access, preparation, intended use, quality, and
  privacy.
- Security covers CVSS 2/3/4, EPSS, Exploit Catalog, SSVC, and VEX
  assessments.
- Software owns files, packages, SBOMs, snippets, and artifacts.

Licensing is divided into common Licensing data, text-formatted
SimpleLicensing data, and parseable machine-readable ExpandedLicensing data.
Information outside the defined profiles belongs under the separate
`extension` namespace.

## Build an SPDX 3 Lite document (spdx-3.0.1-specification)

### SPDX Lite document and SBOM roots

A Lite `SpdxDocument` requires `creationInfo`, `spdxId`, `element`, and
`rootElement`. `element` must include at least one SBOM object, and its roots
should be SBOM objects.

Each Lite `/Software/Sbom` likewise requires `creationInfo`, `spdxId`,
`element`, and `rootElement`, with at least one `/Software/Package` in
`element` and package objects preferred as roots. Document `dataLicense` and
`name` are recommended rather than mandatory.

### SPDX Lite package and license minimums

A Lite `/Software/Package` requires:

- `copyrightText`;
- `creationInfo`;
- `name`;
- `packageVersion`;
- `spdxId`;
- `suppliedBy`, preferably a `/Core/Agent`; and
- at least one of `downloadLocation` or `packageUrl`.

Exactly one `hasConcludedLicense` and one `hasDeclaredLicense` relationship
must originate from each package and point to
`/SimpleLicensing/AnyLicenseInfo`.

### SPDX Lite supporting records

- Lite `CreationInfo` requires `created`, one or more `createdBy` agents, and
  a `specVersion` fixed to `3.0.*` for a supported patch release.
- Agents require `creationInfo`, `name`, and `spdxId`.
- Hashes require `algorithm` and `hashValue`.
- License expressions and simple licensing texts require `creationInfo`,
  `spdxId`, and respectively `licenseExpression` or `licenseText`.
- Relationships require `creationInfo`, `from`, `relationshipType`, `spdxId`,
  and one or more `to` values.

## Model the SPDX Build profile (spdx-3.0.1-json-schema)

### Build-profile payload

Beyond inherited Element fields, `build_Build` requires only
`build_buildType`. Build ID and times are scalar, while config-source digests,
entrypoints, URIs, environment entries, and parameters are arrays. Digests are
`Hash` records. Environment and parameter items are `DictionaryEntry` records,
whose values may be omitted.

```json
{"@context":"https://spdx.org/rdf/3.0.1/spdx-context.jsonld","type":"build_Build","spdxId":"urn:spdx:build","creationInfo":"urn:spdx:creation","build_buildType":"https://example.test/build/type"}
```

## Model the SPDX AI profile (spdx-3.0.1-json-schema)

### AI-profile payload

`ai_AIPackage` has no AI-specific required property. Autonomy and
sensitive-personal-information values are `yes`, `no`, or `noAssertion`.
Safety risk is `low`, `medium`, `high`, or `serious`.

Energy is separated into optional training, fine-tuning, and inference arrays.
Their entries require a numeric-or-decimal-string quantity and a unit of
`kilowattHour`, `megajoule`, or `other`.

```json
{"ai_energyConsumption":{"type":"ai_EnergyConsumption","ai_trainingEnergyConsumption":[{"type":"ai_EnergyConsumptionDescription","ai_energyQuantity":12.5,"ai_energyUnit":"kilowattHour"}]}}
```

## Model the SPDX Dataset profile (spdx-3.0.1-json-schema)

### Dataset-profile payload

`dataset_DatasetPackage` requires a nonempty `dataset_datasetType` array
chosen from:

```text
audio, categorical, graph, image, noAssertion, numeric, other, sensor,
structured, syntactic, text, timeseries, timestamp, video
```

Its size is a nonnegative integer. Availability is `clickthrough`,
`directDownload`, `query`, `registration`, or `scrapingScript`.
Confidentiality is `amber`, `clear`, `green`, or `red`.
Sensitive-personal-information uses `yes`, `no`, or `noAssertion`.

## Model CycloneDX data and machine learning (cyclonedx-1.6)

### Dedicated data and ML component payloads

A `data` component should carry `data` entries whose required type is
`source-code`, `configuration`, `dataset`, `definition`, or `other`. Entries
can embed or link contents and record classification, sensitive data,
graphics, and governance.

A `machine-learning-model` should carry a model card covering parameters,
datasets, inputs/outputs, metrics, limitations, fairness, and environmental
consumption. Its fixed measurement units are `kWh` and `tCO2eq`.

```json
{"type":"data","name":"training-set","data":[{"type":"dataset","classification":"confidential","contents":{"url":"https://example.test/dataset"}}]}
```

## Model CycloneDX service data governance (cyclonedx-1.6)

### Service data models direction and governance

Every service `data` entry requires a classification and a flow relative to
the service: `inbound`, `outbound`, `bi-directional`, or `unknown`. Source and
destination entries are IRIs or BOM-Link element references.

Governance separates custodians, stewards, and owners. Each responsible party
must choose either an organization or an individual contact.

```json
{"data":[{"flow":"outbound","classification":"restricted","destination":["https://api.example.test/store"],"governance":{"owners":[{"organization":{"name":"Data Office"}}]}}]}
```

## Encode standards and attestations (cyclonedx-1.6)

### Standards, claims, and attestations are first-class BOM data

The root `definitions.standards` collection models standards, hierarchical
requirements, and compliance levels. `declarations` links assessors, targets,
claims, counter-evidence, and evidence through `bom-ref` values and maps
attestations to requirements with 0–1 conformance and confidence scores.

An affirmation signatory must satisfy exactly one branch: an embedded JSF
signature, or an external reference together with an organization.

```json
{"definitions":{"standards":[{"name":"Example Standard","requirements":[{"bom-ref":"req-1","identifier":"AC-1"}]}]},"declarations":{"claims":[{"bom-ref":"claim-1","predicate":"Control is implemented."}],"attestations":[{"map":[{"requirement":"req-1","claims":["claim-1"],"conformance":{"score":1}}]}]}}
```

## Apply distribution constraints (cyclonedx-1.7)

### TLP distribution constraints

`metadata.distributionConstraints.tlp` records the BOM's Traffic Light
Protocol sharing classification and declares `CLEAR` as the default. Its exact
values are `CLEAR`, `GREEN`, `AMBER`, `AMBER_AND_STRICT`, and `RED`.

```json
{"metadata":{"distributionConstraints":{"tlp":"AMBER_AND_STRICT"}}}
```

## Inventory patents and assertions (cyclonedx-1.7)

### Patent inventories and assertions

`definitions.patents` holds patents or patent families. A patent requires
`patentNumber`, two-letter `jurisdiction`, and `patentLegalStatus`; a family
requires `familyId` and may reference member patents.

Components and services can attach `patentAssertions`. Each assertion requires
an `asserter` and one of:

```text
ownership, license, third-party-claim, standards-inclusion, prior-art,
exclusive-rights, non-assertion, research-or-evaluation
```

```json
{"definitions":{"patents":[{
  "bom-ref":"patent-1","patentNumber":"US987654321",
  "jurisdiction":"US","patentLegalStatus":"granted"
}]},"components":[{
  "type":"library","name":"codec",
  "patentAssertions":[{"assertionType":"license","patentRefs":["patent-1"],
    "asserter":{"name":"Acme","url":["https://example.test"]}}]
}]}
```

## Map requirements to OpenCRE (cyclonedx-1.7)

### OpenCRE requirement mappings

A standard requirement can map to one or more OWASP Common Requirements
Enumeration identifiers through `openCre`. Every value must use the exact
`CRE:<digits>-<digits>` form.

```json
{"definitions":{"standards":[{"name":"Example Standard","requirements":[{
  "bom-ref":"requirement-1","identifier":"AC-1","openCre":["CRE:764-507"]
}]}]}}
```
