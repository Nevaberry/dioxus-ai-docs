# Remote forms

## Values and schemas

### Deep-partial nested values

Remote form `.value()` and `.set(...)` use deep-partial types
(`sveltekit-2.53.0`), so callers can provide only the nested descendants that
are present. Nested sets are rendered correctly during SSR.

### Match schemas to HTML payloads

Unchecked controls are omitted from HTML form data. Remote forms therefore
warn when a checkbox-like boolean input is not optional in its schema. Empty
file inputs are also omitted from the remote form payload
(`sveltekit-2.66.0`).

Optional fields work with TypeScript's `exactOptionalPropertyTypes` setting
(`sveltekit-2.67.0`); do not weaken form schemas merely to accommodate that
compiler mode.

### Chain preflight before repeated forms

A `preflight(...)` schema applies correctly when chained before `for(...)`.
This ordering can be used safely for repeated form instances.

## Submission and navigation

### Respect redirect targets

Redirects produced by a remote form submission honor the form's `target`
attribute (`sveltekit-2.54.0`), including targets that navigate a different
browsing context.

### Use submission state directly

Remote forms expose `submitted` (`sveltekit-2.69.0`). Drive submitted-state UI
from that property instead of maintaining duplicate local state.

## Reset and validation state

Form reset is deferred by one tick. A reset also clears validation issues and
touched-field state, returning validation UI to a pristine state rather than
retaining stale feedback.

`fields.branch.issues()` returns `undefined` when issues exist only on a
descendant such as `fields.branch.leaf`. Do not treat a leaf issue as an
additional branch-level issue.

## File uploads

Form handling supports streaming file uploads, allowing a file to be processed
without buffering the complete upload first.
