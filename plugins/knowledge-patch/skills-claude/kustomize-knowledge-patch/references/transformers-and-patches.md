# Transformers and Patch Files

## Image transformer

The `images` transformer updates image references in Kubernetes image
volumes. These references are transformed alongside the workload image fields
that were already supported. (5.7.0)

Account for both locations when checking the rendered result of an image
change:

- workload image fields;
- image references used by image volumes.

## Empty or comment-only patch files

Patch files made up only of blank lines, multiple newlines, or comments are
accepted instead of failing the build. (5.7.0)

This applies when the file contains no effective patch content because all of
its content is whitespace or comments.

## Multiple strategic-merge deletes

One patch file can contain multiple strategic-merge patches that each use
`$patch: delete`. This no longer causes Kustomize to panic. (5.7.0)

Multiple resource deletions can therefore remain together in one
strategic-merge patch file.
