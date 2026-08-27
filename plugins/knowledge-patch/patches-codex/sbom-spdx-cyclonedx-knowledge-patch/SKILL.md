---
name: sbom-spdx-cyclonedx-knowledge-patch
description: SBOM / SPDX / CycloneDX
version: null
license: MIT
metadata:
  author: Nevaberry
---


# SBOM: SPDX and CycloneDX Knowledge Patch

Use this skill when authoring, reviewing, converting, or validating SPDX or
CycloneDX documents. Start from the document's declared format and version,
then apply the matching model, serialization, and conformance rules. Do not
infer semantic conformance from a successful JSON Schema pass.

## Reference index

| Reference | Topics |
| --- | --- |
| [Document identity and serialization](references/document-identity-and-serialization.md) | Namespaces, external documents, media types, JSON-LD envelopes, canonical JSON, BOM-Link, extensions |
| [Components, dependencies, and provenance](references/components-dependencies-and-provenance.md) | Packages, files, snippets, checksums, relationships, lifecycles, evidence, formulations, citations |
| [Licensing, VEX, and cryptography](references/licensing-vex-and-cryptography.md) | Missing-license semantics, license-choice shapes, vulnerability status, assessments, cryptographic assets |
| [Profiles, standards, and specialized data](references/profiles-standards-and-specialized-data.md) | Lite and optional profiles, minimum elements, data and AI payloads, declarations, patents, TLP, OpenCRE |
| [Schema validation and automation](references/schema-validation-and-automation.md) | Schema gaps, exact enums, semantic validation, local commands, `sbom-utility`, `sbomcheck` |

## First identify the document contract

Before changing a BOM:

1. Read the declared format and exact version from the document.
2. Determine the serialization: SPDX `tag:value`, JSON, JSON-LD, RDF, YAML,
   or CycloneDX JSON/XML/Protocol Buffers.
3. For SPDX 3, identify every claimed profile; Core is always required.
4. Resolve every imported or sibling schema before validating.
5. Run structural validation and then the applicable semantic and
   minimum-element checks.
6. Verify identity uniqueness, reference targets, graph completeness, and
   cross-field rules separately.

Keep version-sensitive spellings exact. Property names, enum values, tags,
media-type parameters, and JSON-LD compact names are not interchangeable
across serializations or specification generations.

## Breaking and deprecated forms

### CycloneDX shape changes

- In CycloneDX 1.6, `licenses` is either a list of license objects or one
  expression object. In 1.7 it may mix licenses and expressions and contain
  multiple expressions. Validate against the selected schema instead of
  normalizing both versions to one shape.
- In 1.6, replace the deprecated metadata tool array with the object holding
  component/service arrays. Replace `metadata.manufacture`, component
  `author`, component `modified`, and single-object identity evidence with
  their preferred forms.
- In 1.7 cryptography, use `ellipticCurve`,
  `certificateFileExtension`, and typed `relatedCryptographicAssets`.
  Replace reference-only protocol arrays with structured transforms.
- `versionRange` is only legal on a 1.7 external runtime component and is
  mutually exclusive with `version`. Never set `isExternal` on
  `metadata.component`.

### SPDX compatibility traps

- New SPDX 2 review data is an annotation with type `REVIEW`; the legacy
  review-information section exists only for old compatibility.
- In SPDX 2.3 JSON, operating-system package purpose is
  `OPERATING_SYSTEM`; `tag:value` uses `OPERATING-SYSTEM`.
- SPDX 2.3 generic XML is not a supported lossless serialization even though
  a suggested `.spdx.xml` filename appears in the specification.
- SPDX 3 non-Core compact names use a lowercase profile prefix plus `_`;
  properties with multi-value cardinality remain arrays even with one item.
- SPDX 3 canonical serialization is deterministic single-line JSON, not
  merely minified JSON.

## Validation rules that prevent false confidence

### SPDX 2.3

The draft-07 JSON Schema has a deliberately weak root minimum and omits many
lexical and cross-field constraints. After schema validation, check at least:

- `DocumentNamespace` uniqueness and syntax;
- SPDX identifiers and all references;
- declared version and data-license values;
- timestamps and checksum text;
- `FilesAnalyzed`-dependent package fields;
- snippet pointer coordinates;
- required `DESCRIBES` relationships; and
- SPDX Lite or other policy requirements.

### SPDX 3

JSON-LD conformance is a two-stage process:

1. Validate structure against the draft-2020 JSON Schema.
2. Validate meaning against the ontology and SHACL restrictions.

The schema accepts semantically incomplete graphs, permissive URI and numeric
forms, and some generic extension payloads that bypass dedicated extension
shapes. Check imports and external SPDX IDs manually when the semantic tool
cannot interpret an `SpdxDocument` import.

### CycloneDX

The schema validates structure, not global reference existence or `bom-ref`
uniqueness. Some typed unions and cryptographic asset/detail combinations also
need semantic checks. Local validation must provide imported SPDX-license,
signature, and cryptography definition schemas as required by the selected
document version.

## High-value authoring rules

### Identity and revisions

- Give each SPDX 2 document revision a new absolute, fragment-free namespace.
- Bind an SPDX external-document reference to its namespace and checksum.
- Give a CycloneDX BOM a lowercase UUID serial number and increment `version`
  whenever that same BOM is modified.
- Use `urn:cdx:<uuid>/<version>#<bom-ref>` for cross-BOM element references;
  do not use that prefix for local `bom-ref` values.
- In SPDX 3, distinguish an Element's `spdxId` from the optional `@id` on
  non-element records.

### Unknown, absent, and empty are different

- SPDX `NONE` asserts absence; `NOASSERTION` records intentional uncertainty.
- An omitted relationship list makes no completeness claim.
- In CycloneDX, an empty `dependsOn` declares no direct dependencies, while
  omitting the graph entry leaves dependencies unknown.
- In SPDX 3, explicit absence uses `NoneElement` as the sole relationship
  target; `NoAssertionElement` represents an intentional lack of assertion.
- Keep composition completeness separate from the edges in a dependency
  graph.

### Files and packages

- `FilesAnalyzed` defaults to true. When false, omit files,
  `PackageVerificationCode`, and `PackageLicenseInfoFromFiles`.
- Do not confuse a package verification code with a package artifact
  checksum: the first is derived from sorted file digests; the second hashes
  the artifact itself.
- In `tag:value`, ordering carries containment: standalone files precede
  packages, package files immediately follow their package, and snippets
  immediately follow their file.
- Preserve single-versus-array cardinality exactly in SPDX 3.

### Licenses and vulnerability status

- Treat omitted SPDX license and copyright fields as `NOASSERTION` only where
  the model defines that default; use `NONE` only for an explicit assertion
  that no applicable information exists.
- Keep a CycloneDX version-range status separate from the VEX analysis state.
  A `not_affected` analysis should carry a justification.
- SPDX 3 VEX subclasses have uneven schema minima; enforce the policy-required
  impact statement, justification, and relationship semantics yourself.
- Treat advisory catalogs and other external-reference enumerations as
  creation-time snapshots, not live security data.

## Practical workflow

### Author or update a BOM

1. Select the exact product, version, profile, and serialization.
2. Establish document identity and revision behavior.
3. Add components, services, files, snippets, and relationships.
4. Encode licenses, security assessments, and completeness explicitly.
5. Add provenance, lifecycle, governance, or specialized profile data.
6. Validate locally with every imported schema available.
7. Run semantic, reference-integrity, and minimum-element checks.
8. Revalidate after conversion; lossless translation is a separate guarantee
   from source-document validity.

### Review an existing BOM

Look first for:

- schema-version mismatch;
- deprecated properties or version-incompatible shapes;
- missing imported schemas;
- references that validate lexically but do not resolve;
- omitted-versus-empty graph mistakes;
- profile claims unsupported by required elements;
- schema-valid but impossible dates, unbounded scores, or malformed digests;
- incorrect license-list/expression composition; and
- security status without supporting analysis or justification.

### Automate validation

Use validation exit codes, machine-readable diagnostics, explicit error
limits, and bounded failing-value output. Pin the intended schema or named
variant in automation. Keep alternate JSON Schemas separate from custom
CycloneDX policy checks, and select SPDX 3 plus the FSCT3 policy explicitly
when those are the intended minimums.

## Output discipline

When producing guidance or patches:

- state the format and version whose spelling or behavior is being used;
- distinguish schema requirements from semantic conformance;
- preserve `NONE`, `NOASSERTION`, unknown, omitted, and empty semantics;
- avoid inventing extension keys where the model provides a properties or
  extension mechanism;
- include required sibling/imported schemas in validation instructions; and
- call out manual checks that the chosen validator cannot perform.
