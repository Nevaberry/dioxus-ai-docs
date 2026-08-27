# Source Verification Summaries and Provenance

SLSA 1.2 uses a Source Verification Summary Attestation (VSA) as the
interoperable statement of a source revision's verified Source level. The
underlying Source Provenance remains defined by the source control system
(SCS).

## Issuance and availability

An SCS must issue a Source VSA for every revision claimed at Source L1 or
higher. Without a Source VSA, the revision is Source L0.

The VSA must be retrievable by a consumer authorized for the revision. At L2
and above, it must be based on Source Provenance issued by the SCS.

## Revision, reference, and repository identity

The Verification Summary separates three kinds of identity:

- `subject.digest` identifies the immutable revision;
- `subject.annotations.sourceRefs` lists references that pointed to that
  revision; and
- `predicate.resourceUri` identifies the repository.

Use fully qualified reference names for Git, such as `refs/heads/main`. Keep
the repository identity separate from a branch or tag reference and from the
revision digest.

`subject.uri` is an investigation link only. It may help a person open a
source browser, but it is not a policy input and must not replace either the
digest or `resourceUri` during verification.

When the SCS uses non-cryptographic revision identifiers, it must define a
canonical digest type that also incorporates the repository. This prevents a
bare identifier from being treated as globally meaningful when it is only
unique inside one repository.

## Level fields

`verifiedLevels` contains only the highest Source level met. Do not enumerate
all implied lower levels in that array.

`dependencyLevels` may report levels for dependencies such as Git submodules.
These dependency claims are distinct from the level of the subject revision;
do not combine them into one effective subject level without an explicit
consumer policy.

## Example Verification Summary

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

In this shape:

- the in-toto statement wraps one source-revision subject;
- `gitCommit` carries the immutable revision identifier;
- `sourceRefs` records the fully qualified branch reference;
- `resourceUri` carries repository identity;
- the verifier identifies itself and records its verification time;
- the predicate identifies the policy and its result; and
- `verifiedLevels` reports only the highest met Source level.

The example's `subject.uri` remains informational even though it points at the
same revision represented by the digest.

## Source Provenance boundary

Source VSAs provide an interoperable summary, but SLSA does not prescribe one
underlying Source Provenance format. Each SCS must document every provenance
format it emits and the meaning of that format.

For protected branch or tag updates, the SCS must issue Source Provenance
contemporaneously with the update. It must make that provenance available to
consumers authorized for the revision.

A VSA authority must know the expected issuer for every provenance type it
accepts and validate that issuer. Merely parsing a recognized format is not
enough to establish that the expected SCS produced it.

## Producer procedure

1. Capture the protected branch or tag update as it occurs.
2. Issue the SCS-defined Source Provenance contemporaneously.
3. Preserve the update time, actor, and new revision required for named-ref
   updates at L2 and above.
4. Build the VSA subject from the immutable revision digest and the references
   that pointed to it.
5. Put stable repository identity in `resourceUri`.
6. Evaluate the documented Source policy and place only the highest met level
   in `verifiedLevels`.
7. Add dependency levels separately when they are available and useful.
8. Publish both the summary and, subject to authorization, its supporting
   provenance through consumer-accessible paths.

## Consumer procedure

1. Fetch the Source VSA using authorization for the target revision.
2. Match `resourceUri` to the expected repository.
3. Match `subject.digest` to the expected immutable revision.
4. Inspect `sourceRefs` for the fully qualified protected branch or tag context
   required by policy.
5. Ignore `subject.uri` for policy matching; use it only for investigation.
6. Read `verifiedLevels` as the single highest Source level reported.
7. Evaluate `dependencyLevels` separately from the subject's level.
8. At L2 and above, ensure the authority based the VSA on SCS-issued Source
   Provenance.
9. Validate the expected issuer for each accepted provenance type.
10. Apply onboarding and control-continuity boundaries before relying on the
    claim for the target revision.

## Common policy errors

- Treating a web URL in `subject.uri` as immutable revision identity.
- Matching a digest without also establishing repository identity when the
  revision identifier is non-cryptographic.
- Recording abbreviated Git branch names instead of fully qualified refs.
- Listing every implied Source level instead of only the highest met level.
- Folding a dependency's level into the subject revision's own claim.
- Assuming that a shared VSA schema means all SCS provenance schemas are the
  same.
- Accepting provenance based on format alone without checking the expected
  issuer.
- Issuing provenance after the fact rather than contemporaneously with the
  protected branch or tag update.
