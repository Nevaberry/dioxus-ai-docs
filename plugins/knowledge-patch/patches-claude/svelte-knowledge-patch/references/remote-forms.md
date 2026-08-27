# Remote forms

The versioned form behavior in this reference is attributed to
`sveltekit-2.53.0`, `sveltekit-2.54.0`, `sveltekit-2.66.0`,
`sveltekit-2.67.0`, and `sveltekit-2.69.0`.

## Values and schemas

### Deep-partial values

Remote form `.value()` and `.set(...)` accept deep-partial types. A nested form
shape can omit descendant fields, and nested value updates render correctly
during server-side rendering.

### Boolean and file fields

A remote form warns when a boolean input is not optional in its schema, matching
HTML's omission of unchecked controls. Model checkbox-like values as optional
unless the application supplies them separately. Empty file inputs are omitted
from remote form data.

### Exact optional property types

Optional remote-form schema fields work with TypeScript's
`exactOptionalPropertyTypes`; projects using that mode do not need to weaken
their schema types.

## Validation and state

### Chain preflight before repeated forms

A `preflight(...)` schema works when chained before `for(...)`. Repeated form
instances can use that ordering without losing the preflight schema.

### Submission state

Read the form's `submitted` property when UI needs to react to whether the form
has been submitted. Avoid maintaining duplicate local submission state.

### Reset behavior

Reset is deferred by one tick. A reset also clears validation issues and touched
fields, returning validation UI to a pristine state.

### Branch issue scoping

`fields.branch.issues()` returns `undefined` when an issue exists only on a
descendant such as `fields.branch.leaf`. Handle leaf issues at the leaf rather
than treating them as branch-level issues too.

## Submission behavior

### Redirect targets

A redirect returned by a remote form submission honors the form's `target`
attribute, including targets that navigate another browsing context.

### Stream file uploads

Form handling supports streaming file uploads. Upload processing does not have
to buffer the complete file before handling it.
