---
name: slsa-knowledge-patch
description: SLSA
version: 1.2
license: MIT
metadata:
  author: Nevaberry
---

# SLSA Knowledge Patch

Use this skill when designing, implementing, or evaluating SLSA Source-track
controls, Source Verification Summary Attestations (VSAs), or the Source
Provenance behind those summaries. Keep source-security claims separate from
Build-track claims and evaluate each claim for the exact revision, repository,
and named-reference context involved.

## Reference index

| Reference | Topics |
| --- | --- |
| [source-levels-and-controls.md](references/source-levels-and-controls.md) | Source-track scope, actor roles, levels L1-L4, continuity, protected references, review, and exceptional history removal |
| [verification-summaries-and-provenance.md](references/verification-summaries-and-provenance.md) | Source VSA production and consumption, Verification Summary fields, digest handling, dependency levels, Source Provenance, and issuer validation |

## Critical Source-track boundaries

- Rate how a source revision was created independently of how an artifact was
  built. A Build-track level does not imply a Source-track level, or vice versa.
- Begin a branch's Source claims at its onboarding revision. Do not extend the
  claims to revisions that precede onboarding.
- Treat a lapse in any claimed control as a continuity break. A later restored
  control begins a new claim at a new revision; it does not repair the gap.
- Require a Source VSA for every revision claimed at Source L1 or higher. In the
  absence of a VSA, treat the revision as Source L0.
- At Source L2 and above, base the VSA on Source Provenance issued by the source
  control system (SCS).
- Keep the interoperable VSA separate from the underlying Source Provenance.
  SLSA defines the summary format but leaves provenance formats to each SCS.
- Never use `subject.uri` as a policy input. It is an investigation link;
  `subject.digest` and `predicate.resourceUri` carry the revision and repository
  identities used for verification.

## Actor-role quick reference

| Role | Permitted trust-relevant behavior |
| --- | --- |
| Administrator | Can perform privileged operations. Do not count administrative power as ordinary review approval. |
| Trusted person | May propose and approve changes under the SCS's controls. |
| Trusted robot | Has an identity and code that cannot be unilaterally influenced; may receive an explicit perpetual policy exception at L4. |
| Untrusted person | May propose or review changes but cannot approve them or administer the system. |

Model the roles explicitly in policy. A comment or review from an untrusted
person can inform a change, but it cannot satisfy an approval requirement.

## Source-level quick reference

### L1: identifiable, inspectable revisions

Require all of the following:

- a suitable version-control or source-control system;
- a stable repository identity;
- an immutable, unique revision identity;
- human-readable diffs; and
- a Source VSA for the revision.

L1 establishes that a consumer can identify and inspect the revision and
obtain its verification summary. It does not imply the controlled-access,
history, or identity-management guarantees of L2.

### L2: controlled and attributable history

Add all of the following:

- controlled access;
- reliable, immutable history;
- identity management;
- continuity of the claimed controls; and
- contemporaneous Source Provenance.

For every named-reference update, record the update time, the actor, and the
new revision. When the revision model has ancestry, allow a branch to move
only to a descendant. Protect tags from both movement and deletion.

### L3: continuously enforced protected references

Require protected named references and documented technical controls that are
enforced continuously. Record the enforced controls in SCS attestations.

Organization-defined VSA properties are allowed only under the
`ORG_SOURCE_` prefix. Use `ORG_SOURCE_INTERNAL_` for internal properties.
Do not place organization-specific properties in an unprefixed namespace.

### L4: two trusted people per protected-branch change

Require agreement from two trusted people using one of these patterns:

1. a trusted uploader and a different trusted reviewer; or
2. two trusted reviewers.

Bind approval to the final revision in its specific repository and branch
context. Any later edit invalidates the earlier approval. Moving reviewed
content to a different repository or branch context also requires review
again.

A trusted robot can bypass the ordinary two-person pattern only through an
explicit perpetual policy exception. Do not infer that exception from the
robot merely being automated or trusted.

## Exceptional history removal at L2 and above

Expunge history only for legal or privacy compliance and only through a
documented process. Track both the requests and the resulting actions, and
the process should log the removal. The specification recommends requiring an
administrator plus another trusted person to trigger it.

Do not treat this narrow exception as permission for ordinary force-pushes,
tag rewrites, or deletion of inconvenient history.

## Source VSA production checklist

1. Issue one Source VSA for every revision claimed at L1 or higher.
2. Make it fetchable by a consumer authorized for that revision.
3. At L2 or higher, derive it from SCS-issued Source Provenance.
4. Put the immutable revision identity in `subject.digest`.
5. Put references that pointed to the revision in
   `subject.annotations.sourceRefs`; use fully qualified references for Git.
6. Identify the repository with `predicate.resourceUri`.
7. Use `subject.uri` only as a human investigation link.
8. Put only the highest satisfied Source level in `verifiedLevels`.
9. Report dependency levels, such as Git submodule levels, separately in
   `dependencyLevels` when applicable.

If revision identifiers are not cryptographic, define a canonical digest type
that incorporates the repository as well as the revision. A bare
non-cryptographic revision identifier is not sufficient across repositories.

## Verification Summary field map

| Field | Meaning and policy treatment |
| --- | --- |
| `subject[].digest` | Immutable source revision identity; use for policy matching. |
| `subject[].annotations.sourceRefs` | Named references that pointed to the revision; fully qualify Git refs. |
| `subject[].uri` | Investigation link only; never make authorization or level decisions from it. |
| `predicate.resourceUri` | Stable repository identity used with the revision digest. |
| `predicate.verifier.id` | Identity of the authority that produced the verification result. |
| `predicate.timeVerified` | Time at which verification was performed. |
| `predicate.policy.uri` | Policy evaluated by the verifier. |
| `predicate.verificationResult` | Result of applying the stated policy. |
| `predicate.verifiedLevels` | Only the highest Source level met by this revision. |
| `predicate.dependencyLevels` | Optional separate levels for dependencies such as Git submodules. |

## Minimal Source VSA shape

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "uri": "https://github.com/acme/app/commit/abc123",
    "digest": {"gitCommit": "abc123"},
    "annotations": {"sourceRefs": ["refs/heads/main"]}
  }],
  "predicateType": "https://slsa.dev/verification_summary/v1",
  "predicate": {
    "verifier": {"id": "https://scs.example/source-verifier"},
    "timeVerified": "2025-11-24T12:00:00Z",
    "resourceUri": "git+https://github.com/acme/app",
    "policy": {"uri": "https://scs.example/source-policy"},
    "verificationResult": "PASSED",
    "verifiedLevels": ["SLSA_SOURCE_LEVEL_3"]
  }
}
```

Adapt the identifiers and policy to the SCS, but preserve the separation
between revision identity, repository identity, reference context, and the
human-oriented investigation URI.

## Source Provenance responsibilities

The SCS owns the underlying Source Provenance formats. For each supported
format, it must:

- document the format and its meaning;
- issue provenance contemporaneously with the protected branch or tag update;
- make it available to consumers authorized for the revision; and
- give the VSA authority enough issuer information to validate the expected
  issuer for that provenance type.

Do not require all SCS implementations to emit one universal provenance
schema. Interoperability occurs at the Source VSA summary layer; provenance
remains SCS-defined and must be interpreted according to the SCS's
documentation.

## Consumer verification flow

1. Identify the expected repository and immutable revision.
2. Fetch the Source VSA through an authorized path.
3. Match `predicate.resourceUri` to the repository and `subject.digest` to the
   revision; do not substitute `subject.uri` for either check.
4. Inspect `sourceRefs` when policy depends on a protected branch or tag.
5. Confirm that `verifiedLevels` contains one highest satisfied Source level.
6. Keep dependency claims separate from the subject revision's own level.
7. At L2 and above, confirm that the VSA authority used SCS-issued Source
   Provenance and validated the expected issuer for each provenance type.
8. Apply onboarding and continuity boundaries before accepting the claimed
   level for an older or post-lapse revision.

## Policy review checklist

- Separate Source-track and Build-track decisions.
- Bind every claim to a repository, immutable revision, and relevant ref.
- Record onboarding revisions and any later continuity restart points.
- Assign actors to administrator, trusted-person, trusted-robot, or untrusted
  roles based on actual authority and influence.
- Verify the complete requirement set for the claimed level; do not treat one
  strong control as a substitute for another.
- For L4, verify two-person agreement against the final revision and exact
  branch context.
- Treat robot exceptions and compliance-driven history removal as explicit,
  documented exceptions.
- Use the indexed references for the full control and attestation details.
