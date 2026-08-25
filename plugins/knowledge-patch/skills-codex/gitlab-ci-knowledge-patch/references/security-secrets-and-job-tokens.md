# Security, Secrets, and Job Tokens

## Restrict job-token permissions

Since 18.0, projects on GitLab.com and GitLab Self-Managed can use beta
fine-grained CI job-token permissions in all tiers. Limit a token to specific
project resources rather than granting the triggering user's full permissions.
Use this control for least-privilege CI/CD jobs.

## Store and request scoped secrets

GitLab Secrets Manager enters open beta in 19.0 for Premium and Ultimate
customers on GitLab.com and GitLab Self-Managed. Project and group Owners can
store and retrieve secrets scoped to their project or group. Access can be
limited to pipeline jobs that explicitly request those secrets.

The service remains subject to the beta support policy and might not be ready
for production use. Account for that status when choosing it for critical
workloads.

## Push to another project with a job token

Since 19.0, `CI_JOB_TOKEN` can push to a different project when all of these
conditions hold:

- The target project opts in.
- The user who started the pipeline has at least the Developer role in the
  target project.
- The `allow_push_to_allowlisted_projects` feature flag is enabled.

The feature flag is disabled by default in 19.0.

## Apply the 19.2.1 security patch

GitLab 19.2.1 fixes 13 vulnerabilities, including three high-severity issues,
and should be installed immediately on affected self-managed 19.2 systems.
The equivalent fixed releases are 19.1.3 and 19.0.5. GitLab.com is already
patched, and GitLab Dedicated customers do not need to act.

## Assess the CI/CD and authorization fixes

The three high-severity paths fixed in 19.2.1 could allow:

- A Developer to retrieve unauthorized information through Workhorse.
- An authenticated user to alter another user's CI/CD configuration through
  pipeline schedule inputs.
- An unauthenticated user to cause denial of service through merge request
  discussions.

The release also fixes a protected-branch approval bypass, unauthorized access
to pipeline test reports, cross-project disclosure through Duo Code Review,
and a Duo Workflows bypass of administrator tool-governance policies.
