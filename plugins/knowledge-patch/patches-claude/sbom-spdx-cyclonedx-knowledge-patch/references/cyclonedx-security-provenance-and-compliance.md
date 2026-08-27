# CycloneDX security, provenance, and compliance

Use this reference for VEX, workflows, standards and attestations,
cryptographic assets, distribution controls, and patent declarations.

## Vulnerability exploitability

The VEX rules in this section are attributed to `cyclonedx-1.6`.

Every vulnerability target in `affects` references a component or service. It
may list single versions or Package URL `vers` ranges. Range status is
`affected`, `unaffected`, or `unknown`, and defaults to `affected`.

The separate `analysis` object records states such as `not_affected`,
`false_positive`, and `exploitable`, along with standardized justifications and
responses, detail, and first- and last-issued timestamps. A `not_affected`
analysis should include a justification.

```json
{
  "id": "CVE-2024-0001",
  "affects": [{
    "ref": "pkg",
    "versions": [{
      "range": "vers:npm/>=1.0.0|<2.0.0",
      "status": "unaffected"
    }]
  }],
  "analysis": {
    "state": "not_affected",
    "justification": "code_not_reachable",
    "detail": "The vulnerable path is not invoked."
  }
}
```

## Build and deployment formulation

Top-level `formulation` contains formulas with transient components and
services plus independently triggered workflows. Every workflow and task
requires:

- `bom-ref`.
- Deployment-context `uid`.
- A `taskTypes` array, with values including `build`, `scan`, `test`,
  `deliver`, and `deploy`.

The model can also preserve task dependency and runtime-topology graphs,
triggers and conditions, ordered command steps, typed inputs and outputs, and
shareable workspaces and volumes.

```json
{
  "formulation": [{
    "workflows": [{
      "bom-ref": "workflow-build",
      "uid": "run-42",
      "taskTypes": ["build"],
      "tasks": [{
        "bom-ref": "task-build",
        "uid": "build-42",
        "taskTypes": ["build"],
        "steps": [{"commands": [{"executed": "npm ci"}]}]
      }]
    }]
  }]
}
```

## Standards, claims, and attestations

The root `definitions.standards` collection models standards, hierarchical
requirements, and compliance levels. `declarations` connects assessors,
targets, claims, counter-evidence, and evidence through `bom-ref` values.
Attestations map to requirements and may carry zero or one conformance score
and zero or one confidence score.

An affirmation signatory must satisfy exactly one of:

1. An embedded JSF signature.
2. An external reference together with an organization.

```json
{
  "definitions": {
    "standards": [{
      "name": "Example Standard",
      "requirements": [{"bom-ref": "req-1", "identifier": "AC-1"}]
    }]
  },
  "declarations": {
    "claims": [{
      "bom-ref": "claim-1",
      "predicate": "Control is implemented."
    }],
    "attestations": [{
      "map": [{
        "requirement": "req-1",
        "claims": ["claim-1"],
        "conformance": {"score": 1}
      }]
    }]
  }
}
```

## Cryptographic asset inventory

### Typed assets

The base cryptographic model here is attributed to `cyclonedx-1.6`.

A component with type `cryptographic-asset` uses
`cryptoProperties.assetType` equal to `algorithm`, `certificate`, `protocol`,
or `related-crypto-material`. Dedicated details cover:

- Algorithm primitives, parameter sets, functions, and security levels.
- Certificate validity and key references.
- Protocol cipher suites.
- Key and related-material lifecycle and protection.

Only `assetType` is schema-required. The schema has no conditional that binds
that value to the corresponding detail object, so validate consistency
semantically.

```json
{
  "type": "cryptographic-asset",
  "name": "AES-256-GCM",
  "bom-ref": "crypto-aes",
  "cryptoProperties": {
    "assetType": "algorithm",
    "algorithmProperties": {
      "primitive": "ae",
      "parameterSetIdentifier": "256",
      "mode": "gcm",
      "cryptoFunctions": ["encrypt", "decrypt"]
    }
  }
}
```

### Migrated field names and references

The migration rules here are attributed to `cyclonedx-1.7`.

Use:

| Current field | Replaces |
| --- | --- |
| `algorithmProperties.ellipticCurve` | `curve` |
| `certificateFileExtension` | `certificateExtension` |
| Typed `relatedCryptographicAssets` | Certificate `signatureAlgorithmRef` and `subjectPublicKeyRef`, key-material `algorithmRef`, protocol `cryptoRefArray` |

Local schema validation must resolve `cryptography-defs.schema.json`, which
provides the allowed `algorithmFamily` and `ellipticCurve` values.

```json
{
  "certificateProperties": {
    "certificateFileExtension": "pem",
    "relatedCryptographicAssets": [
      {"type": "algorithm", "ref": "crypto-signature"},
      {"type": "publicKey", "ref": "crypto-public-key"}
    ]
  }
}
```

### Structured protocol cryptography

Protocol assets can model IKEv2 transform objects for `encr`, `prf`, `integ`,
`ke`, and `auth`, plus `esn`. Arrays containing only cryptographic references
are deprecated. Cipher suites can additionally list `tlsGroups` and
`tlsSignatureSchemes`.

```json
{
  "protocolProperties": {
    "type": "ike",
    "ikev2TransformTypes": {
      "encr": [{
        "name": "ENCR_AES_GCM_16",
        "keyLength": 256,
        "algorithm": "crypto-aes-gcm"
      }],
      "ke": [{"group": 31, "algorithm": "crypto-x25519"}],
      "esn": true
    }
  }
}
```

### Certificate lifecycle and extensions

Certificate properties may carry predefined lifecycle states
`pre-activation`, `active`, `suspended`, `deactivated`, `revoked`, or
`destroyed`, or custom named states. Creation, activation, deactivation,
revocation, and destruction each have separate timestamps.

`certificateExtensions` accepts either a recognized common extension name and
value or a custom extension name with an optional value.

```json
{
  "certificateProperties": {
    "certificateState": [{
      "state": "active",
      "reason": "production certificate"
    }],
    "activationDate": "2025-10-21T12:00:00Z",
    "certificateExtensions": [{
      "commonExtensionName": "keyUsage",
      "commonExtensionValue": "digitalSignature"
    }]
  }
}
```

## Distribution constraints

This behavior is attributed to `cyclonedx-1.7`.

`metadata.distributionConstraints.tlp` declares the BOM's Traffic Light
Protocol sharing classification. It defaults to `CLEAR`; exact values are
`CLEAR`, `GREEN`, `AMBER`, `AMBER_AND_STRICT`, and `RED`.

```json
{"metadata": {"distributionConstraints": {"tlp": "AMBER_AND_STRICT"}}}
```

## Patent inventories and assertions

The patent model is attributed to `cyclonedx-1.7`.

`definitions.patents` contains patents or patent families:

- A patent requires `patentNumber`, a two-letter `jurisdiction`, and
  `patentLegalStatus`.
- A family requires `familyId` and may reference its member patents.

Components and services can attach `patentAssertions`. Each assertion requires
an `asserter` and an assertion type:

```text
ownership, license, third-party-claim, standards-inclusion, prior-art,
exclusive-rights, non-assertion, research-or-evaluation
```

```json
{
  "definitions": {
    "patents": [{
      "bom-ref": "patent-1",
      "patentNumber": "US987654321",
      "jurisdiction": "US",
      "patentLegalStatus": "granted"
    }]
  },
  "components": [{
    "type": "library",
    "name": "codec",
    "patentAssertions": [{
      "assertionType": "license",
      "patentRefs": ["patent-1"],
      "asserter": {"name": "Acme", "url": ["https://example.test"]}
    }]
  }]
}
```

## OpenCRE requirement mappings

A standard requirement may map to one or more OWASP Common Requirements
Enumeration identifiers using `openCre`. Every identifier must exactly match
`CRE:<digits>-<digits>`.

```json
{
  "definitions": {
    "standards": [{
      "name": "Example Standard",
      "requirements": [{
        "bom-ref": "requirement-1",
        "identifier": "AC-1",
        "openCre": ["CRE:764-507"]
      }]
    }]
  }
}
```
