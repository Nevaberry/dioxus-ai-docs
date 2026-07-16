# Queries and Runtime

## SQL identifier and alias escaping

Values passed to `sql.identifier()` and `sql.as()` are properly escaped
starting with 0.45.2.

Earlier releases could leave these values improperly escaped.

That behavior could expose an application to SQL injection when it used
either helper.

Upgrade when a project uses:

- `sql.identifier()`
- `sql.as()`

## Security review

Search the repository for both helper forms.

For each call site:

1. Identify the value passed to the helper.
2. Determine whether the value is fixed in source or supplied dynamically.
3. Confirm which `drizzle-orm` version executes the query.
4. Upgrade if the project can run the earlier escaping behavior.
5. Exercise the call site with nontrivial identifier or alias values.

Treat upgrading as the remediation for the helper behavior.

Do not describe application-side checks as a substitute for the corrected
escaping implementation.

## Scope

The corrected behavior applies specifically to values passed to the two
helpers named above.

Keep broader query-security findings separate unless repository evidence
connects them to these helpers.

When reporting the change, name the helper, the executing ORM version,
and whether its value is dynamic.
