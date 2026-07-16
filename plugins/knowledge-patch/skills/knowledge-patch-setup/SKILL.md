---
name: knowledge-patch-setup
description: Detect, activate, or deactivate bundled knowledge patches.
---

# Knowledge Patch Setup

Use this skill when the user wants to set up, activate, deactivate, or verify knowledge patches for a project, server, VPS, or working session.

## Workflow

1. Load `knowledge-patch:using-knowledge-patch` if it is not already loaded.
2. Read `../../catalog/patches.json`, `../../catalog/aliases.json`, and `../../catalog/detection.json`.
3. Inspect the current project and, when relevant, the server environment. A plain detection file signal checks path existence; `glob::marker` requires the matching file to contain that literal marker. Use curated terms only as supporting evidence, not as a substitute for stronger file or manifest evidence.
4. Recommend the narrowest useful patch set. Use each catalog `short_label` in user-facing activation messages. For server-looking evidence, ask whether admin guidance is desired before treating service patches as active.
5. If the user approves activation, write priority state only. Do not copy skill files, install separate plugins, or fetch anything from the network.
6. If the user asks to deactivate or remove patches, remove the resolved patch names and their activation reasons. If the user says `none` or asks to clear all activation, write an empty `active_patches` list and empty `activation_reasons` object.

Preferred project state path:

```text
.knowledge-patch/activation.json
```

User-level fallback:

```text
$XDG_STATE_HOME/knowledge-patch/activation.json
```

Use this JSON shape:

```json
{
  "schema_version": 1,
  "active_patches": [
    "traefik-knowledge-patch"
  ],
  "activation_reasons": {
    "traefik-knowledge-patch": "manual: user is editing Traefik routing"
  },
  "updated_at": "2026-07-06T00:00:00Z"
}
```

Preserve unrelated fields if a state file already exists. Manual activation reasons should not be overwritten by weaker automatic detections.

## Constraints

- Everything works offline.
- Bundled tech patches already live under `skills/`.
- Activation changes priority and routing, not installation.
- Deactivation removes priority state, not bundled skills.
- Hooks are optional. Manual use through this skill and `using-knowledge-patch` is the reliable path.
