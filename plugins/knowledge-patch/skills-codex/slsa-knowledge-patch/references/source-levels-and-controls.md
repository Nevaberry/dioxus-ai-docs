# Source Levels and Controls

SLSA 1.2 introduces a Source track that rates how a source revision was
created. Apply it independently of the Build track: neither track supplies or
implies a level in the other.

## Claim scope and continuity

A branch's Source claims begin at its onboarding revision. Revisions that
predate onboarding are outside the claim even if they remain reachable from
the branch.

Continuity is per claimed control. When a control lapses, its prior claim does
not bridge the gap. Restoring the control starts a new continuous period at a
new revision. Record onboarding and restart revisions so consumers can decide
whether a particular revision falls inside a valid claim period.

Evaluate approvals in repository and branch context. Approval of equivalent
content elsewhere is not automatically approval of the revision under review.

## Actor model

### Administrators

Administrators can perform privileged operations. Policies should distinguish
this operational power from the trusted-person approvals used for ordinary
protected-branch changes.

### Trusted people

Trusted people may propose and approve changes. At L4, policies use distinct
trusted people to provide the required two-person agreement.

### Trusted robots

A trusted robot has an identity and code that cannot be unilaterally
influenced. At L4, a policy may grant such a robot an explicit perpetual
exception. Trust or automation alone does not create the exception; the
policy must state it.

### Untrusted people

Untrusted people may propose or review changes, but they cannot approve
changes or administer the system. Their reviews therefore cannot satisfy a
trusted approval requirement.

## Source L1

L1 requires all of these properties:

- a suitable version-control or source-control system;
- stable repository identity;
- immutable, unique revision identity;
- human-readable diffs; and
- a Source Verification Summary Attestation for the revision.

The Source VSA is mandatory for the claim. A revision without one is Source
L0, regardless of which other controls the repository uses.

## Source L2

L2 adds all of these properties:

- controlled access;
- reliable, immutable history;
- identity management;
- continuity of claimed controls; and
- Source Provenance issued contemporaneously with the relevant update.

Every update to a named reference must record:

1. the time of the update;
2. the actor; and
3. the new revision.

Where revisions have ancestry, branches must move only to descendants. Tags
must be protected against both movement and deletion. From L2 onward, the
Source VSA must be based on SCS-issued Source Provenance.

## Source L3

L3 requires protected named references and continuously enforced, documented
technical controls. The SCS records the controls it enforced in attestations;
informal practice without continuous technical enforcement is insufficient.

The SCS may include organization-defined properties in a Source VSA, subject
to namespace rules:

- use `ORG_SOURCE_` for organization-defined Source properties; and
- use `ORG_SOURCE_INTERNAL_` for internal properties.

Do not add organization-specific VSA properties without the required prefix.

## Source L4

Every protected-branch change needs agreement from two trusted people. Either
of these patterns satisfies that structure:

- a trusted uploader plus a different trusted reviewer; or
- two trusted reviewers.

Approval is narrow. It covers the final revision in the specific repository
and branch context in which it was reviewed. Later edits require review again,
as does moving the reviewed content to another repository or branch context.

A trusted robot may receive an explicit perpetual policy exception. The
exception is not implicit and should be evaluated separately from the normal
two-person paths.

## Legal or privacy history expungement

At L2 and above, history may be expunged only for legal or privacy compliance.
Use a documented process that:

- tracks requests;
- tracks the actions taken in response; and
- should log the removal.

The specification recommends requiring an administrator together with
another trusted person to trigger the process. This is a constrained
compliance exception, not a general relaxation of immutable-history,
descendant-only branch movement, or tag protection.

## Level evaluation procedure

1. Resolve the repository and immutable revision being evaluated.
2. Determine whether it is at or after the branch's onboarding revision.
3. Check whether any required control lapsed before that revision; if so,
   locate the new continuity start revision.
4. Verify every requirement at the claimed level and all lower levels.
5. Confirm the Source VSA exists; otherwise return Source L0.
6. For L2 and above, verify contemporaneous SCS-issued Source Provenance and
   named-reference update records.
7. For L3, verify continuous technical enforcement and attested controls.
8. For L4, verify two distinct trusted people against the final revision and
   its exact repository and branch context, unless an explicit trusted-robot
   exception applies.
