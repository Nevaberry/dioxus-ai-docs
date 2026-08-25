# Edit Commands

## File-backed label edits

`kustomize edit add labels` handles the `-f` flag in the same way as
`edit add commonLabels`. Flag-dependent label edits are therefore consistent
between the two commands. (5.6.0)

## Multiple labels without selector updates

`kustomize edit add labels` can add multiple labels together with
`--without-selector`. The combination no longer fails with a duplicate-key
error. (5.8.0)

This multiple-label and `--without-selector` combination is accepted.
