# Nevaberry Plugins

Plugins and knowledge patches for coding agents. Knowledge patches fill gaps left by model training cutoffs.

## Install

Install the meta-plugin to auto-detect your project's stack and install matching patches:

```
/install-plugin nevaberry-plugins/knowledge-patch
```

Or:

```sh
npx skills add https://github.com/nevaberry/nevaberry-plugins --skill knowledge-patch
```

Then run `/knowledge-patch-setup` to scan your project (package.json, Cargo.toml, go.mod, etc.) and install matching patches automatically.

### Manual install

Install individual patches directly — useful before rewriting to a new technology:

```
/install-plugin nevaberry-plugins/rust-knowledge-patch
/install-plugin nevaberry-plugins/dioxus-knowledge-patch
```

Or:

```sh
npx skills add https://github.com/nevaberry/nevaberry-plugins --skill dioxus-knowledge-patch
```

## How it works

AI models have training cutoffs. After that, APIs change, functions get deprecated, and new features ship. Knowledge patches contain only what changed: curated, verified diffs against baseline model knowledge.

When loaded, the patch is checked **before** writing code for that technology. This helps prevent outdated APIs, deprecated patterns, and broken implementations.

## Coverage

**Languages & runtimes:** Bun, Deno, Elixir, Gleam, Go, Kotlin, Node.js, Python, Rust, Swift, TypeScript, Zig

**Frontend & app frameworks:** Angular, Astro, Dioxus, Flutter, Leptos, Next.js, Nuxt, React, React Router, SolidJS, Svelte, Tauri, Vite, Vue

**Backend & server frameworks:** Axum, Django, FastAPI, Hono, Rails, Spring Boot, tRPC

**Data & persistence:** Drizzle, pgvector, PostGIS, PostgreSQL, Prisma, SQLite, SQLx

**Auth & identity:** Auth.js, Better Auth, Clerk, Supabase, WorkOS, ZITADEL

**AI, cloud & APIs:** AWS SDK, GCP, LangChain, PyTorch, Stripe, Vercel AI SDK

**Tooling & infrastructure:** Biome, Caddy, Docker, Kubernetes, Nginx, Playwright, Podman, Tailwind CSS, Terraform, Tokio, Traefik, Vitest

**Linux distros:** AlmaLinux, Arch, CentOS Stream, Debian, Fedora, openSUSE/SLES, RHEL, Rocky, Ubuntu
