# Knowledge Patch

`knowledge-patch` is an offline plugin that ships knowledge patches for specific technology versions as native Claude Code and Codex skills. The bundled patches are available immediately after installation; no downloader is involved.

Knowledge patches are derived from the respective projects' official release notes and documentation. This project is not affiliated with or endorsed by those projects.

## Install

Use the Claude Code or Codex instructions in the repository `README.md`. Then invoke the native setup skill as `/knowledge-patch:knowledge-patch-setup` in Claude Code or `$knowledge-patch-setup` in Codex; a natural-language setup request works in either CLI.

## Canonical skills and compatibility commands

- Codex uses `$knowledge-patch-setup`, `$knowledge-patch-status`, or a natural-language request.
- Claude Code uses `/knowledge-patch:knowledge-patch-setup`, `/knowledge-patch:knowledge-patch-status`, or a natural-language request.
- `/knowledge-patch:setup`, `/knowledge-patch:activate`, and `/knowledge-patch:status` remain Claude Code compatibility aliases. They delegate to native skills and are not the canonical implementation.

## Skills

- `using-knowledge-patch` is the gateway skill. Load it before writing, reviewing, debugging, or administering a technology that may have a bundled patch.
- `knowledge-patch-setup` supports setup, activation, and deactivation workflows.
- `knowledge-patch-status` supports status checks.
- Technology patch skills are listed in `catalog/patches.json` and the generated gateway index at `skills/using-knowledge-patch/references/patch-index.md`.

## Activation

Activation is priority state, not installation. The preferred project state file is `.knowledge-patch/activation.json`; user-level state can live at `$XDG_STATE_HOME/knowledge-patch/activation.json`, and `$KNOWLEDGE_PATCH_STATE` can point to a specific state file.

All bundled technology patches already live under `skills/`. Activation tells agents which patches the user intentionally wants prioritized. Deactivation removes matching patch names and reasons from that state; `none` clears all active patch names and activation reasons.

## SessionStart Hook

`hooks/session-start` is optional. When either CLI runs the SessionStart hook from `hooks/hooks.json`, it can add gateway guidance and active patch names to the session context. Manual or natural-language use through the native skills remains the reliable path.

The `startup|resume|clear|compact` matcher is deliberate. Resume re-reads activation state so changes made since the previous session replace stale dynamic guidance. The hook prefers `$CLAUDE_PROJECT_DIR` for project state and exits silently if state is malformed or an unexpected error occurs. Hooks are hints only; native skills continue to work when hooks are disabled, untrusted, or unavailable.

## Detection Signals

In `catalog/detection.json`, a plain file glob means that the path's existence is evidence. A signal in `glob::marker` form requires a matching file whose contents contain the literal marker. Content markers keep shared manifests such as `package.json` and `Cargo.toml` from activating unrelated patches.

## Versioning

The knowledge-patch plugin uses the form `COMPAT.DATE.PATCH`:

- `COMPAT` indicates backwards compatibility.
- `DATE` is the UTC build date as `yyyymmdd`.
- `PATCH` counts builds within that date, starting at `0`.

A new version is minted only when shipped content actually changes; `catalog/build.json` records the version and a content hash over every shipped file. Technology coverage is versioned separately: `covered_through` in the catalogs, mirrored in each skill's frontmatter `version`, states the upper boundary a patch covers.

## Shipped Layout

- `.claude-plugin/marketplace.json` exposes the Claude Code marketplace entry.
- `.agents/plugins/marketplace.json` exposes the Codex marketplace entry.
- `plugins/knowledge-patch/.claude-plugin/plugin.json` is the Claude Code plugin manifest and explicitly declares native skills and hooks.
- `plugins/knowledge-patch/.codex-plugin/plugin.json` is the Codex plugin manifest and explicitly declares native skills and hooks, but no commands component.
- `plugins/knowledge-patch/skills/` contains the gateway skill, helper skills, and technology patch skills.
- `plugins/knowledge-patch/catalog/` contains patch, alias, detection, and build catalogs.
- `plugins/knowledge-patch/commands/` contains the three Claude Code legacy compatibility aliases.
- `plugins/knowledge-patch/hooks/` contains the optional SessionStart hook.
