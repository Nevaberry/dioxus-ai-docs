---
name: sbom-spdx-cyclonedx-knowledge-patch
description: SBOM / SPDX / CycloneDX
version: null
license: MIT
metadata:
  author: Nevaberry
---


# SBOM, SPDX, and CycloneDX

Use this skill when producing, transforming, validating, or reviewing SPDX and
CycloneDX SBOMs. Start by identifying the declared format, specification
version, serialization, and intended conformance profile. Keep structural
schema validation separate from semantic and policy checks.

## Reference index

| Reference | Topics |
| --- | --- |
| [SPDX document and package authoring](references/spdx-document-and-package-authoring.md) | SPDX 2 document structure, package fields, relationships, SPDX 3 collections, identities, and Lite roots |
| [SPDX serialization and validation](references/spdx-serialization-and-validation.md) | SPDX 2 JSON and `tag:value`, SPDX 3 JSON-LD and RDF, schema limits, canonical form, and validation commands |
| [SPDX profiles and domain records](references/spdx-profiles-and-domain-records.md) | Profile conformance, supporting records, vocabularies, Software, Build, AI, Dataset, Security, VEX, and licensing |
| [CycloneDX core authoring](references/cyclonedx-core-authoring.md) | BOM identity, links, extensions, lifecycle, components, licensing, dependencies, evidence, services, and data attribution |
| [CycloneDX security, provenance, and compliance](references/cyclonedx-security-provenance-and-compliance.md) | VEX, formulation, attestations, cryptographic assets, patents, certificate lifecycle, TLP, and OpenCRE |
| [Validation tooling and interoperability](references/validation-tooling-and-interoperability.md) | Offline schema selection, exit codes, custom validation, NTIA, CISA FSCT3, and command examples |

## Breaking differences and deprecations

### Select behavior by the declared specification version

- Do not treat nearby CycloneDX releases as schema-compatible. In 1.6,
  `licenses` is either a list of license objects or exactly one expression.
  In 1.7, the array may mix licenses and multiple expressions.
- In CycloneDX 1.7, only an external runtime component may use `versionRange`;
  it is mutually exclusive with `version`, and `metadata.component` cannot be
  external.
- SPDX 2.3 `PrimaryPackagePurpose` spells the tag value
  `OPERATING-SYSTEM`, while JSON uses `OPERATING_SYSTEM`.
- SPDX 3 compact names are profile-sensitive: Core names are unprefixed, while
  other profiles use lowercase profile prefixes such as `software_Package`.
- A property with multi-value cardinality in SPDX 3 must be serialized as an
  array even when it contains one item.

### Replace deprecated fields

- New SPDX review information is an annotation with type `REVIEW`; the old
  review-information section exists only for compatibility.
- For CycloneDX metadata tools, use an object with `components` or `services`,
  not the deprecated tool array.
- Replace CycloneDX `metadata.manufacture` with
  `metadata.component.manufacturer`, component `author` with `authors` or
  `manufacturer`, component `modified` with `pedigree`, and scalar identity
  evidence with an array.
- For CycloneDX cryptography, replace `curve` with `ellipticCurve` and
  `certificateExtension` with `certificateFileExtension`.
- Replace certificate `signatureAlgorithmRef` and `subjectPublicKeyRef`,
  key-material `algorithmRef`, and protocol `cryptoRefArray` with typed
  `relatedCryptographicAssets`.
- Use structured IKEv2 transform objects instead of deprecated arrays of bare
  cryptographic references.

## Validation rules that prevent false confidence

### Schema success is not conformance

- SPDX 2.3 JSON Schema omits several normative requirements, including
  document namespace and cross-reference integrity.
- SPDX 3 conformance needs both JSON Schema validation and semantic validation
  with the ontology and its SHACL restrictions.
- CycloneDX schemas validate many shapes but do not establish global
  `bom-ref` uniqueness, target existence, or all conditional consistency.
- Enforce lexical, referential, cardinality, and cross-field requirements in a
  semantic pass even when the schema accepts the document.

### Resolve all imported schemas

- SPDX 2.3 JSON uses draft-07.
- SPDX 3 JSON Schema validation uses draft 2020 mode.
- CycloneDX validation may require sibling SPDX-license, JSF-signature, or
  cryptography definition schemas.
- When possible, let a version-aware validator select its bundled schema from
  BOM metadata instead of forcing a nearby schema.

### Treat validator exit codes as an API

For `sbom-utility`, distinguish success (`0`), application error (`1`), and
validation failure (`2`). In automation, request JSON errors, raise the default
error limit when needed, and suppress large failing values with
`--error-value=false`.

## SPDX quick reference

### Document identity and external references

- Give every SPDX 2 document revision a new, unique absolute
  `DocumentNamespace` URI. It must have a scheme and no fragment, but need not
  resolve.
- Bind every external document reference to a local `DocumentRef-` identifier,
  the external namespace, and a checksum.
- In SPDX 3, distinguish the logical `SpdxDocument` from its serialized
  `Artifact`; connect them with `serializedInArtifact`.
- Use the exact global JSON-LD context and encode references as IRIs or blank
  node identifiers where allowed.

### Package analysis state

- `FilesAnalyzed` defaults to `true`.
- When false, the package contains no files and must omit both
  `PackageVerificationCode` and `PackageLicenseInfoFromFiles`.
- A package verification code is a digest over sorted file digests; a package
  checksum is a digest of the package artifact. Do not substitute one for the
  other.
- Omitted license and copyright fields often mean `NOASSERTION`; `NONE` is a
  positive assertion that no applicable information exists.

### Relationships and completeness

- In SPDX 2, a `DESCRIBES` relationship is required when the document has
  multiple packages or standalone files.
- `NONE`, `NOASSERTION`, omission, and a partial relationship list communicate
  different knowledge states.
- In SPDX 3, relationships are Elements with one `from`, one type, and one or
  more `to` values.
- If `NoneElement` is used, it must be the only target.
- An SPDX 3 collection with elements needs roots, and neither collection field
  may contain an `SpdxDocument`.

### SPDX Lite

- Build the required document or SBOM root, package, creation information,
  agents, hashes, licensing records, and relationship records as a connected
  graph.
- Each Lite package needs exactly one concluded-license relationship and one
  declared-license relationship to simple licensing information.
- Do not infer full-profile support from Lite conformance, or support for one
  optional profile from another.

## CycloneDX quick reference

### BOM identity and references

- Prefer a lowercase `urn:uuid:` serial number and increment integer `version`
  when modifying the same BOM.
- A BOM-Link is `urn:cdx:<uuid>/<positive-version>` with optional
  `#<bom-ref>`; local `bom-ref` values should not begin with `urn:cdx:`.
- Use supported `properties` arrays for extension data. Repeated property names
  are valid.

### Dependency and composition meaning

- A dependency with an empty `dependsOn` has no direct dependencies.
- Omitting a component from the dependency graph leaves its dependencies
  unknown.
- `provides` does not imply use.
- Composition completeness applies only to explicitly named assembly or
  dependency references and is not transitive.

### Licensing

- Choose the license shape for the declared CycloneDX version before emitting
  data.
- Preserve the distinction between an SPDX identifier, a free-form license
  name, and an expression.
- In composable license arrays, use `bom-ref` for reusable choices and
  `expressionDetails` to attach evidence to individual identifiers.

### Evidence, services, and provenance

- Validate the required inner shape of identities, analysis methods,
  occurrences, call-stack frames, and annotations.
- Model service-data flow relative to the service and choose either an
  organization or an individual for each governance party.
- Use formulation workflows and tasks for executable build or deployment
  provenance; both need references, run identifiers, and task types.
- Use citations for field-level attribution and satisfy their exclusive
  pointer-or-expression rule.

## Recommended workflow

1. Detect the BOM format, declared version, serialization, and profile.
2. Resolve the matching primary schema and all imported schemas.
3. Run structural validation in the schema's declared dialect.
4. Run semantic checks for references, uniqueness, conditional fields,
   normative cardinality, and profile rules.
5. Run the required minimum-elements or organizational policy checker.
6. Preserve the validator's distinct application and validation-failure exit
   states in automation.
7. Review cross-document identifiers, checksums, and revision identities.
8. When converting formats, verify that the supported source and destination
   representations can carry the same information without loss.

## Output review checklist

- Declared format and version agree with the selected schema.
- Exact property names and enum spellings match the serialization.
- Closed objects contain no arbitrary extension keys.
- All external schemas and contexts resolve in the validation environment.
- Identifiers are unique where required and every reference resolves or is
  intentionally external.
- Required roots, relationships, licensing assertions, and completeness states
  are present.
- Dates pass both lexical and real calendar checks.
- Hash algorithms, digest text, score ranges, and vectors receive semantic
  validation where schemas are permissive.
- Cross-version fields and deprecated aliases are absent.
- Validation, conformance, and policy results are reported separately.
