---
name: using-knowledge-patch
description: Route technology work to matching bundled knowledge patches.
---

# Using Knowledge Patch

Use this gateway when a task involves a technology that may have a bundled knowledge patch. The plugin registers only this gateway and two helper skills; technology patch bodies live in a non-discovered runtime-specific tree. It does not download patches or copy them into another skill directory.

## Routing Rules

1. Before writing, reviewing, debugging, planning, or administering a patched technology, read the matching patch body from the runtime-specific patches tree at the path resolved through the Finding Patches steps below.
2. Determine the project's pinned technology version from its manifest first; consult its lockfile or configuration only when the manifest does not pin it. For `coverage_kind` `versioned` or `range`, compare the project version with `covered_through`, apply only notes introduced at or below the project version, and state that the patch may be stale when the project is newer. Trust project reality—its manifest, code, tests, and current behavior—over stale guidance. For `rolling` or `multi-product`, `covered_through` is JSON null and must not be used for a version comparison. State the coverage kind, inspect the coverage metadata, and prefer project manifests, code, and tests.
3. If the user manually activated patches, treat that as confirmed intent and read those patches before related work.
4. If multiple patches apply, read the relevant set. Do not read every patch just because the catalog exists.
5. Within the applicable version floor, knowledge patches override stale model memory when they conflict. Follow the loaded patch and mention the current behavior when it matters.
6. If no exact patch exists, continue normally and say that no bundled patch matched when that affects confidence.

## Finding Patches

Do not keep or inline a full patch list in this gateway. Resolve patches in this order:

1. Read `../../catalog/index.md` (about 660 tokens) to determine whether a matching patch exists.
2. Read `../../catalog/index.json` to resolve the matching display name to its patch id.
3. Read `../../patches-claude/<id>/SKILL.md`, substituting the resolved id.

Use `references/patch-index.md` and `../../catalog/patches.json` only when coverage or other detailed catalog metadata is needed. Use `../../catalog/aliases.json` for manual names, aliases, and fuzzy activation, and `../../catalog/detection.json` for setup/status detection hints.

## Activation State

Activation is priority state, not installation. A typical state file is:

```json
{
  "schema_version": 1,
  "active_patches": [
    "postgresql-knowledge-patch",
    "docker-knowledge-patch"
  ],
  "activation_reasons": {
    "postgresql-knowledge-patch": "manual: user plans to write SQL",
    "docker-knowledge-patch": "detected: docker-compose.yml"
  }
}
```

Check `$KNOWLEDGE_PATCH_STATE`, then `.knowledge-patch/activation.json` in the current project, then `$XDG_STATE_HOME/knowledge-patch/activation.json` when the user asks for setup, activation, deactivation, or status.

## VPS And Admin Work

For server, VPS, deployment, or machine-administration tasks, consider whether OS, init system, container, proxy, database, TLS, and observability patches apply. Look for concrete evidence such as `/etc/os-release`, systemd, Docker or Podman, compose files, Nginx/Caddy/Traefik config, PostgreSQL config, TLS assets, SSH context, CI/container hints, and project deployment files.

Ask before service-impacting admin changes. Do not assume a normal Linux shell is production. Manual activation beats automatic detection.

## Hook Behavior

The session-start hook is only a hint layer. It may inject this gateway's core rule and active patch names, but the plugin must work fully when hooks are disabled, untrusted, unavailable, or never fire. Resume deliberately re-reads activation state so changes made since the previous session replace stale dynamic guidance.
