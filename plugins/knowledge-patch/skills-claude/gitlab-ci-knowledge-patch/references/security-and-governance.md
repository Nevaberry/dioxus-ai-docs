# Security, Secrets, and Governance

## Limit CI job tokens to project resources

Since 18.0, projects on GitLab.com and GitLab Self-Managed can use beta fine-grained
job-token permissions to limit a CI job token to specific project resources instead
of inheriting the triggering user's full permissions. The beta is available in all
tiers. Grant only the resources the job actually needs and retain an explicit
review step while adopting the beta.

## Store pipeline secrets in GitLab Secrets Manager

Since 19.0, GitLab Secrets Manager is in open beta for Premium and Ultimate
customers on GitLab.com and GitLab Self-Managed. Project and group Owners can store,
retrieve, and reference secrets scoped to their project or group. Limit access to
pipeline jobs that explicitly request each secret. The service remains under the
beta support policy and may not be ready for production-critical secrets.

## Enforce centrally scheduled pipeline policies

Since 19.2, scheduled pipeline execution policies can define a schedule once in a
security policy project and enforce it across every project in scope without
changing each project's `.gitlab-ci.yml`.

Each policy launches a separate pipeline on a daily, weekly, or monthly cadence,
independent of commit activity. Configure the time zone, distribute execution within
the allowed window, and select the target branch centrally.

## Automatically remediate vulnerable dependencies

Since 19.2, dependency scanning auto-remediation is available in beta on GitLab.com,
GitLab Self-Managed, and GitLab Dedicated. When enabled, it monitors projects and
opens merge requests that update vulnerable dependencies to safe patch or minor
versions by default.

The credit-consuming Agentic Breaking Change Resolution option also permits major
upgrades. It can analyze a failed update pipeline, the dependency changelog, and
code usage; commit compatibility fixes to the same merge request; and rerun the
pipeline until it passes. Review generated major-version changes and credit policy
before enabling that path.

## Apply the 19.2.1 security patch

GitLab 19.2.1 fixes 13 vulnerabilities, including three high-severity issues.
Install it immediately on affected Self-Managed 19.2 systems. The equivalent fixed
releases are `19.1.3` and `19.0.5`. GitLab.com is already patched, and GitLab
Dedicated customers do not need to act.

## Assess affected CI/CD and authorization paths

The high-severity issues fixed in 19.2.1 could allow:

- A Developer to retrieve unauthorized information through Workhorse.
- An authenticated user to change another user's CI/CD configuration through
  pipeline schedule inputs.
- An unauthenticated user to cause denial of service through merge-request
  discussions.

The patch also closes a protected-branch approval bypass, unauthorized pipeline
test-report access, cross-project information disclosure in Duo Code Review, and a
Duo Workflows bypass of administrator tool-governance policies. Include these paths
in exposure review and incident scoping, even if the three high-severity cases do
not match the deployment's initial threat model.
