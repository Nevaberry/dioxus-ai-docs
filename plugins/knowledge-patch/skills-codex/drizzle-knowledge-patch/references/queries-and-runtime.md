# Queries and Runtime

## Secure SQL identifiers and aliases

Starting with `drizzle-orm@0.45.2`, values passed to `sql.identifier()` and
`sql.as()` are properly escaped.

Earlier releases could leave those values improperly escaped. When an
identifier or alias contains untrusted input, that behavior can expose the
application to SQL injection.

Upgrade to a corrected ORM release whenever either helper is used. Do not
treat input filtering as a substitute for the helper's escaping correction.

## Audit procedure

Search the codebase for both affected helpers:

```text
sql.identifier(
sql.as(
```

At each call site:

1. Identify the installed `drizzle-orm` version.
2. Trace where the identifier or alias value originates.
3. Distinguish hard-coded values from runtime input.
4. Upgrade if the code runs on a release without the correction.
5. Retest values containing characters that require escaping.
6. Record the upgrade as a security-relevant change.

Prioritize call sites fed by request data, user configuration, stored data,
or any other value outside the static query definition.

## Review guidance

Do not conclude that a call site is safe merely because ordinary identifier
or alias values work. The corrected behavior matters specifically for values
that require escaping.

When reporting the issue, name `sql.identifier()` or `sql.as()` directly and
state whether the value is dynamic. This keeps the affected query boundary
clear and makes the required package upgrade actionable.

After upgrading, keep application-level validation that enforces business
rules, but rely on the corrected helper behavior for SQL escaping.
