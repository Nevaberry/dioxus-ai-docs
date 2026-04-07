# Nevaberry Plugins

Knowledge patches for Claude Code and Codex. They fill gaps in model training data for 40+ technologies.

## Install

### Claude Code

Install the meta-plugin to auto-detect your project's stack and install matching patches:

```
/install-plugin nevaberry-plugins/knowledge-patch
```

Then run `/knowledge-patch-setup` to scan your project (package.json, Cargo.toml, go.mod, etc.) and install matching patches automatically.

### Codex

This repo also publishes a Codex plugin bundle at `plugins/knowledge-patch/` plus a Codex marketplace entry at `.agents/plugins/marketplace.json`.

Install the `knowledge-patch` plugin from that marketplace, then invoke the `knowledge-patch-setup` skill to scan your project and install matching `*-knowledge-patch` skills into `$CODEX_HOME/skills`. The setup flow can also add the optional Codex `SessionStart` hook in repo or user scope.

### Manual install

Install individual patches directly in Claude Code when you already know what technology you need:

```
/install-plugin nevaberry-plugins/supabase-knowledge-patch
/install-plugin nevaberry-plugins/clerk-knowledge-patch
```

## How it works

Claude's training data has a cutoff date. After that, APIs change, functions get deprecated, and new features ship. Knowledge patches contain only what changed — curated, verified diffs against Claude's baseline knowledge.

When loaded, the patch is checked **before** writing code for that technology. This prevents outdated APIs, deprecated patterns, and broken code.

## Coverage

**Languages & runtimes:** Bun, Deno, Go, Node.js, Python, Rust, TypeScript, Zig

**Web frameworks:** Astro, Dioxus, Leptos, Next.js, React, Svelte, Vite

**Databases & ORMs:** Drizzle, PostGIS, PostgreSQL, Prisma, SQLite, SQLx

**Auth & platforms:** Auth.js, Better Auth, Clerk, Supabase, WorkOS, Zitadel

**Infrastructure:** Docker, Podman, Tailwind, Vercel AI SDK

**Linux distros:** AlmaLinux, Arch, CentOS Stream, Debian, openSUSE/SLES, RHEL, Rocky, Ubuntu
