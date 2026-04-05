---
description: Create a symlink so .claude/memory/ in your project points to Claude Code's system memory directory
allowed-tools: [Bash]
---

# Claude Memory Symlink

Run the bundled script to create a symlink from `.claude/memory/` in the project root to Claude Code's system memory directory (`~/.claude/projects/{encoded-repo-path}/memory/`).

## Instructions

1. Run the script:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/claude-memory-symlink.sh
```

2. Show the output to the user verbatim.

3. If the script exits with a non-zero status, show the error and suggest:
   - If "not a git repository": the user needs to run this from inside a git repo
   - If "could not remove" directory: there are conflicting files that need manual resolution — show which files remain and suggest the user resolve duplicates, then re-run the command
