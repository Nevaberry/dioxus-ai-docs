# Queries and Runtime

## Identifier and alias escaping

Since `0.45.2`, Drizzle properly escapes values passed to:

- `sql.identifier()`
- `sql.as()`

Earlier releases could leave those values improperly escaped. When an
application uses either helper on an affected release, the result can expose
it to SQL injection.

Upgrade the ORM when either helper is used. Do not treat the upgrade as
optional maintenance when the project depends on the corrected escaping.

## Security boundary

The helper implementation must correctly escape the value it receives.

Application-side restrictions can reduce the set of values reaching a query,
but they do not replace corrected escaping in `sql.identifier()` or
`sql.as()`.

Avoid preserving an affected release with local quoting or filtering as the
only protection. Move the project to a release containing the correction.

## Review procedure

1. Record the installed `drizzle-orm` version.
2. Search the query layer for `sql.identifier(`.
3. Search the query layer for `sql.as(`.
4. Trace the values passed to every matching call.
5. Identify values that are not fixed in the static query definition.
6. Upgrade if the installed ORM predates the escaping correction.
7. Retest every affected query path.
8. Record the security-sensitive upgrade in the final report.

Review both helpers. Finding one does not establish that the other is absent.

## Change guidance

Prefer the corrected library behavior over an application-specific escaping
substitute.

Keep the call-site review even after upgrading. The correction makes the
helpers escape their inputs properly; the review establishes where those
security-sensitive inputs enter the query.

When handing off the change, name `sql.identifier()` or `sql.as()` explicitly
so future reviewers can find the relevant surface quickly.

## Verification checklist

- The installed `drizzle-orm` contains the escaping correction.
- Every `sql.identifier()` call has been inventoried.
- Every `sql.as()` call has been inventoried.
- Affected query paths have been rerun after the upgrade.
- The handoff identifies the SQL injection risk addressed by the change.
