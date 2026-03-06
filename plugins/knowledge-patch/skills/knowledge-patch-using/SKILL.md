---
name: knowledge-patch-using
description: This skill should be used when starting any session with knowledge patches loaded, or when there is even a 1% chance a task involves a technology with a loaded knowledge patch. Covers "Bun", "TypeScript", "Next.js", "Python", "Rust", "Dioxus", "PostgreSQL", "PostGIS" and any technology with a loaded *-knowledge-patch plugin.
---

## First: Check If Patches Are Installed

Before anything else, check whether the individual knowledge patch skills are actually available in this session. Look at the list of available skills — do any `*-knowledge-patch` skills appear (e.g., `bun-knowledge-patch`, `rust-knowledge-patch`, `typescript-knowledge-patch`)?

**If NO patch skills are available** (only this `using-knowledge-patches` skill exists):

The knowledge patch plugins are not installed yet. Tell the user:

> The knowledge patch meta-plugin is installed, but the individual technology patches are not. Run `/knowledge-patch-setup` to scan your project and install the matching patches.
>
> Available patches: `bun-knowledge-patch`, `typescript-knowledge-patch`, `nextjs-knowledge-patch`, `python-knowledge-patch`, `rust-knowledge-patch`, `dioxus-knowledge-patch`, `postgresql-knowledge-patch`, `postgis-knowledge-patch`

STOP HERE. Do not proceed with the rules below until patches are actually installed.

**If YES, patch skills are available** — proceed with the enforcement rules below.

---

## The Rule

If there is even a 1% chance your task involves a technology with a loaded knowledge patch, you ABSOLUTELY MUST invoke that patch skill BEFORE writing any code.

IF A KNOWLEDGE PATCH EXISTS FOR A TECHNOLOGY YOU ARE WORKING WITH, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.

## What Are Knowledge Patches?

Knowledge patches fill gaps in your training data for rapidly-evolving technologies. They contain:

- **New APIs and syntax** released after your training cutoff
- **Breaking changes** that make your training data dangerous
- **Migration guides** for moving between versions
- **Correct patterns** replacing deprecated approaches

Without patches, you WILL generate outdated, broken, or deprecated code.

## How to Access Patches

Use the `Skill` tool to invoke any available knowledge patch by name:

```
Skill: bun-knowledge-patch
Skill: rust-knowledge-patch
Skill: typescript-knowledge-patch
```

Invoke the relevant patch skill BEFORE writing any code for a patched technology. Even a 1% chance the patch might be relevant means you MUST invoke it. If it turns out not to apply, you lose nothing. If you skip it and it did apply, you generate broken code.

## Red Flags

These thoughts mean STOP — you're about to use outdated information:

| Dangerous Thought | Reality |
|-------------------|---------|
| "I know this API well" | Your training may be months/years behind |
| "This is a simple feature" | Simple features get breaking changes too |
| "I'll just use what I remember" | What you remember may be deprecated |
| "Let me just write the code quickly" | Quick + wrong = wasted time. Check first. |
| "I'm confident about this" | Confidence from training does not equal current accuracy |
| "I need more context first" | Patch check comes BEFORE exploration |

## Priority Order

When multiple information sources conflict:

1. **Knowledge patch content** (highest priority — most current)
2. **Project CLAUDE.md / AGENTS.md instructions** (project-specific guidance)
3. **Your training data** (lowest priority — may be outdated)

Patches always win over training data. No exceptions.

## The Flow

```
Task received
  → Are knowledge patch skills available for this technology?
    → NOT INSTALLED: Tell user to run /knowledge-patch-setup
    → INSTALLED but not invoked: Invoke the patch skill FIRST, then proceed
    → INSTALLED and already loaded: Proceed using patch content
  → Technology has no patch: Proceed normally
```

Do NOT:
- Write code first and check patches later
- Assume you remember the current API
- Skip the patch because the task seems simple
- Rationalize that "this part hasn't changed"
- Claim you'll invoke patches that aren't actually installed
