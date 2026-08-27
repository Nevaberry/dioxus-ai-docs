# Patch files and edit commands

Use this reference for patch-file edge cases and for automation built around
`kustomize edit add labels`.

## Empty and comment-only patch files

From 5.7.0, Kustomize accepts patch files containing only:

- blank lines;
- multiple newlines;
- comments; or
- a combination of those forms with no active patch document.

Such a file no longer fails the build merely because it has no active content.
This is useful when a generated or conditionally maintained patch remains in
the kustomization while all of its entries are inactive.

When investigating a failure involving an inactive patch file, check the
Kustomize version before removing the file or adding a placeholder document.

## Multiple strategic-merge deletes

From 5.7.0, a single patch file can contain multiple strategic-merge patches
that use `$patch: delete`. Kustomize no longer panics on that arrangement.

This permits deletion patches for several resources to stay together in one
file. If the same shape panics under an older binary, upgrading to behavior
that includes the 5.7.0 fix is preferable to assuming the file must always be
split.

Keep the two patch-file improvements distinct:

| File shape | Behavior from 5.7.0 |
| --- | --- |
| Only whitespace, newlines, or comments | Accepted instead of failing the build |
| Multiple strategic-merge `$patch: delete` entries | Processed without a panic |

## `edit add labels` and `-f`

From 5.6.0, `kustomize edit add labels` handles the `-f` flag consistently with
`kustomize edit add commonLabels`.

For scripts that transition from the common-label command to the label
command, retain the intended flag-dependent behavior and verify that the
installed Kustomize includes this consistency change.

## Multiple labels with `--without-selector`

From 5.8.0, `kustomize edit add labels` can add multiple labels in one operation
while using `--without-selector`. The command no longer fails with a
duplicate-key error for that combination.

When label-edit automation reports a duplicate key, separate these questions:

1. Is more than one label being added together?
2. Is `--without-selector` present?
3. Does the active Kustomize include the 5.8.0 fix?

The `-f` change and the `--without-selector` change are independent:

- 5.6.0 aligns `-f` handling between `edit add labels` and
  `edit add commonLabels`;
- 5.8.0 fixes multiple-label use with `--without-selector`.
