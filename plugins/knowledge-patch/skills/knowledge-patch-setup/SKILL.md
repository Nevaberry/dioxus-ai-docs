---
name: knowledge-patch-setup
description: Detect technologies in the current project and install matching `*-knowledge-patch` skills into `$CODEX_HOME/skills`, with an optional Codex `SessionStart` hook in repo or user scope.
---

Use this skill when the user wants to set up knowledge patches for a project or verify which patches match a repo.

## Workflow

1. Resolve the project root with:

   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   ```

2. Scan the project:

   ```bash
   python3 ../../scripts/knowledge_patch_setup.py scan --project-root "<project-root>" --format json
   ```

3. Summarize the detected installable patches and why they matched. Mention that detection is heuristic and the user can also select any available patch manually.

4. If the user did not specify patches to install, ask. Default to all detected patches.

5. If the user did not specify a hook scope, ask whether they want:
   - `repo`: write `<project-root>/.codex/hooks.json` so the hook is shared with the repo
   - `user`: write `$CODEX_HOME/hooks.json` so the hook applies everywhere
   - `none`: install only the skills

   Default to `repo`.

6. Install the requested patches:

   ```bash
   python3 ../../scripts/knowledge_patch_setup.py install --project-root "<project-root>" --all-detected --hook-scope repo --format json
   ```

   If the user selected a subset, replace `--all-detected` with repeated `--patch <name>` flags.

7. Report:
   - installed patch skills
   - `$CODEX_HOME/skills` destination
   - hook config path, if installed
   - that Codex should be restarted to pick up new skills and hooks

## Notes

- Installation is additive. Preserve unrelated skills and unrelated hooks.
- Codex plugins do not currently package hooks through `.codex-plugin/plugin.json`.
- The helper script installs patch skills from the public `Nevaberry/nevaberry-plugins` repo, or from `KP_PUBLIC_REPO` / `--public-repo` during local testing.
- The helper script is the source of truth for detection and installation behavior.
