# Remote forms

## Contents

- [Values and schemas](#values-and-schemas)
- [Payload and reset timing](#payload-and-reset-timing)
- [Preflight and repeated forms](#preflight-and-repeated-forms)
- [Submission and validation state](#submission-and-validation-state)
- [Redirects](#redirects)
- [Streaming uploads](#streaming-uploads)

## Values and schemas

### Deep-partial values

Remote form `.value()` and `.set(...)` use deep-partial types. A nested form
shape can therefore be read or set without specifying every descendant field.
Nested partial sets render correctly during SSR. This behavior is attributed to
`sveltekit-2.53.0`.

### Optional fields

With TypeScript's `exactOptionalPropertyTypes`, optional fields in remote form
schemas retain their intended optional behavior. This compatibility is
attributed to `sveltekit-2.67.0`.

Model boolean controls as optional when the corresponding HTML control can be
unchecked. HTML omits unchecked controls from submission data, and remote forms
warn when such a boolean is required by the schema.

## Payload and reset timing

Empty file inputs are omitted from remote form data instead of being sent as an
empty file value. Form reset happens one tick later, so code observing the same
turn must not assume reset state is already visible. The boolean, empty-file,
and reset-timing behavior is attributed to `sveltekit-2.66.0`.

## Preflight and repeated forms

A `preflight(...)` schema applies correctly when chained before `for(...)`.
Repeated form instances may safely use this order:

```js
form.preflight(schema).for(item)
```

This chaining behavior is attributed to `sveltekit-2.66.0`.

## Submission and validation state

### Submission state

Remote forms expose `submitted`. Use it to render UI based on whether the form
has been submitted instead of mirroring that state locally.

### Reset state

Resetting a remote form clears both validation issues and touched-field state.
The validation UI returns to a pristine state rather than retaining feedback
from the previous submission.

### Branch issue scoping

`fields.branch.issues()` returns `undefined` when issues exist only below that
branch, such as on `fields.branch.leaf`. A descendant issue is not duplicated as
a branch-level issue.

The `submitted`, pristine-reset, and branch-scoping behavior is attributed to
`sveltekit-2.69.0`.

## Redirects

A redirect resulting from a remote form submission honors the form's `target`
attribute. This includes a target that navigates another browsing context. This
behavior is attributed to `sveltekit-2.54.0`.

## Streaming uploads

Form handling supports streaming file uploads. Use streaming where buffering the
entire upload before processing would create unnecessary latency or memory use.
