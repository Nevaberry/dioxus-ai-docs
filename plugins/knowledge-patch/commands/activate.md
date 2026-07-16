---
description: Activate or deactivate bundled patches as priority state.
---

Interpret the patch names, aliases, and action in `$ARGUMENTS`. Read `catalog/aliases.json` and `catalog/patches.json`, and confirm ambiguous matches.

- For activation phrasing, add the matching patch names and reasons to `.knowledge-patch/activation.json`.
- For `deactivate`, `remove`, or equivalent phrasing, remove the matching patch names and their activation reasons.
- If the argument is `none` or clearly asks to clear all activation, set `active_patches` to `[]` and `activation_reasons` to `{}`.

Preserve unrelated state fields. Activation is priority state only. Do not copy skills or fetch patch content.
