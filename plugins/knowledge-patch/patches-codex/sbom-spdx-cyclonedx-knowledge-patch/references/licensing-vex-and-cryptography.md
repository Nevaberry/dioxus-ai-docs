# Licensing, VEX, and Cryptography

Use these rules when encoding license conclusions, vulnerability
exploitability, security assessments, patents, certificates, algorithms, and
protocol cryptography.

## Preserve SPDX 2 license semantics (spdx-2.3-package-model)

### Omitted package license values mean `NOASSERTION`

SPDX 2.3 makes several package license fields optional rather than requiring a
literal `NOASSERTION`. Omission of `PackageLicenseConcluded`,
`PackageLicenseDeclared`, or `PackageCopyrightText` has that meaning, as does
omission of `PackageLicenseInfoFromFiles` when `FilesAnalyzed` is `true` or
absent.

`PackageLicenseInfoFromFiles` must instead be omitted when `FilesAnalyzed` is
`false`. `NONE` remains the explicit assertion that no applicable license or
copyright information exists.

## Preserve SPDX 2 file and snippet defaults (spdx-2.3-json-schema)

### Missing file and snippet license fields imply `NOASSERTION`

For files and snippets, omitting `licenseConcluded` or `copyrightText` has the
meaning `NOASSERTION`. The same applies when a file omits
`licenseInfoInFiles` or a snippet omits `licenseInfoInSnippets`.

## Choose the CycloneDX license shape

### License lists and expressions are exclusive shapes (cyclonedx-1.6)

A `licenses` value is either:

- a list of `{ "license": ... }` objects, where each license has an SPDX `id`
  or free-form `name`; or
- exactly one `{ "expression": ... }` object.

The two forms cannot be mixed. Either form can record `declared` or
`concluded` acknowledgement. License objects can additionally capture
licensor, licensee, purchaser, purchase order, license types, renewal, and
expiration.

```json
{"licenses":[{"expression":"Apache-2.0 AND (MIT OR GPL-2.0-only)","acknowledgement":"concluded"}]}
```

### License choices are composable and referencable (cyclonedx-1.7)

The 1.7 `licenses` array may mix `{license: ...}` and `{expression: ...}`
entries and may contain multiple expressions. Licenses and expressions can
carry `bom-ref`, commercial `licensing` data, and repeatable `properties`.

An expression can use `expressionDetails` to attach a `bom-ref`, text, or URL
to each constituent `licenseIdentifier`.

```json
{"licenses":[
  {"license":{"id":"Apache-2.0","bom-ref":"lic-apache"}},
  {"expression":"MIT OR LicenseRef-Acme","bom-ref":"lic-choice",
   "expressionDetails":[{"licenseIdentifier":"LicenseRef-Acme","url":"https://example.test/license"}]}
]}
```

## Encode CycloneDX VEX (cyclonedx-1.6)

### VEX uses `vers` ranges plus impact analysis

Each vulnerability target in `affects` references a component or service and
can list either single versions or Package URL `vers` ranges. Range status is
`affected`, `unaffected`, or `unknown`, defaulting to `affected`.

`analysis` separately records states such as `not_affected`,
`false_positive`, or `exploitable`, standardized justifications and
responses, detail, and first/last-issued timestamps. A `not_affected`
analysis should include a justification.

```json
{"id":"CVE-2024-0001","affects":[{"ref":"pkg","versions":[{"range":"vers:npm/>=1.0.0|<2.0.0","status":"unaffected"}]}],"analysis":{"state":"not_affected","justification":"code_not_reachable","detail":"The vulnerable path is not invoked."}}
```

## Encode SPDX 3 security assessments (spdx-3.0.1-json-schema)

### Security assessment payloads

The class-local required fields are:

- score and vector for CVSS 2;
- score, severity, and vector for CVSS 3/4;
- percentile and probability for EPSS;
- catalog type, exploited flag, and locator for exploit-catalog assessments;
  and
- decision type for SSVC.

CVSS 3/4 severity is `none`, `low`, `medium`, `high`, or `critical`.
Exploit-catalog type is `kev` or `other`. SSVC decision is `act`, `attend`,
`track`, or `trackStar`. The schema does not bind an assessment subclass to a
corresponding `relationshipType`.

### VEX subclasses encode status

Affected VEX relationships require `security_actionStatement`. Fixed and
under-investigation subclasses add no required status-specific field.
Not-affected relationships require neither an impact statement nor a
justification.

Optional not-affected justification values are:

```text
componentNotPresent
inlineMitigationsAlreadyExist
vulnerableCodeCannotBeControlledByAdversary
vulnerableCodeNotInExecutePath
vulnerableCodeNotPresent
```

## Encode SPDX 3 SimpleLicensing (spdx-3.0.1-json-schema)

### Simple licensing shapes

`simplelicensing_LicenseExpression` requires an unconstrained
`simplelicensing_licenseExpression` string. It may carry a semantic-version
`simplelicensing_licenseListVersion` plus a
`simplelicensing_customIdToUri` array of dictionary mappings.

`simplelicensing_SimpleLicensingText` requires its license text. License
references can also use the constants
`expandedlicensing_NoAssertionLicense` and
`expandedlicensing_NoneLicense`.

## Encode SPDX 3 ExpandedLicensing (spdx-3.0.1-json-schema)

### Expanded licensing operators and sets

Expanded conjunctive and disjunctive sets require at least two
`expandedlicensing_member` entries. An `expandedlicensing_OrLaterOperator`
requires its subject license; an `expandedlicensing_WithAdditionOperator`
requires both its addition and extendable-license subjects.

Custom/listed licenses require `simplelicensing_licenseText`, while
custom/listed additions require `expandedlicensing_additionText`. Member
arrays have no uniqueness constraint.

## Inventory CycloneDX cryptographic assets (cyclonedx-1.6)

### Cryptographic assets have a typed inventory model

A component of type `cryptographic-asset` uses
`cryptoProperties.assetType` of `algorithm`, `certificate`, `protocol`, or
`related-crypto-material`. Dedicated fields describe primitives and security
levels, certificate validity and key references, protocol cipher suites, or
key/material lifecycle and protection.

Only `assetType` is schema-required and no conditional ties it to the matching
detail object, so validate that consistency semantically.

```json
{"type":"cryptographic-asset","name":"AES-256-GCM","bom-ref":"crypto-aes","cryptoProperties":{"assetType":"algorithm","algorithmProperties":{"primitive":"ae","parameterSetIdentifier":"256","mode":"gcm","cryptoFunctions":["encrypt","decrypt"]}}}
```

## Migrate CycloneDX cryptography fields (cyclonedx-1.7)

### Cryptographic field migrations

Use:

- `algorithmProperties.ellipticCurve` instead of deprecated `curve`;
- `certificateFileExtension` instead of `certificateExtension`; and
- typed `relatedCryptographicAssets` instead of certificate
  `signatureAlgorithmRef`/`subjectPublicKeyRef`, key-material `algorithmRef`,
  or protocol `cryptoRefArray`.

Local schema validation must also resolve `cryptography-defs.schema.json`,
which supplies the allowed `algorithmFamily` and `ellipticCurve` values.

```json
{"certificateProperties":{
  "certificateFileExtension":"pem",
  "relatedCryptographicAssets":[
    {"type":"algorithm","ref":"crypto-signature"},
    {"type":"publicKey","ref":"crypto-public-key"}
  ]
}}
```

### Structured protocol cryptography

Protocol assets can describe IKEv2 `encr`, `prf`, `integ`, `ke`, and `auth`
transform objects plus `esn`; the older arrays containing only cryptographic
references are deprecated. Cipher suites can additionally list `tlsGroups`
and `tlsSignatureSchemes`.

```json
{"protocolProperties":{"type":"ike","ikev2TransformTypes":{
  "encr":[{"name":"ENCR_AES_GCM_16","keyLength":256,"algorithm":"crypto-aes-gcm"}],
  "ke":[{"group":31,"algorithm":"crypto-x25519"}],
  "esn":true
}}}
```

### Certificate lifecycle and extensions

Certificate properties can record predefined lifecycle states:

```text
pre-activation, active, suspended, deactivated, revoked, destroyed
```

They can instead use custom named states. Separate timestamps cover creation,
activation, deactivation, revocation, and destruction.
`certificateExtensions` accepts either a recognized common extension name and
value or a custom extension name with an optional value.

```json
{"certificateProperties":{
  "certificateState":[{"state":"active","reason":"production certificate"}],
  "activationDate":"2025-10-21T12:00:00Z",
  "certificateExtensions":[
    {"commonExtensionName":"keyUsage","commonExtensionValue":"digitalSignature"}
  ]
}}
```
