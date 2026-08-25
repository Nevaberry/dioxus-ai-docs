# nevaberry-plugins

Knowledge Patch is a fleet of SKILL.md files that fills current technology
knowledge gaps without mixing target-model extraction streams.

Nevaberry mines technologies such as Kubernetes, Bun, Next.js, RHEL, Dioxus,
and Rust, then compresses each target’s own extraction stream into
topic-organized skills. Claude and Codex receive parallel trees with identical
frontmatter and target-specific bodies.

Why: Claude or Codex loaded with the knowledge-patch plugin uses the newest syntax and API on the first try, instead of confidently generating last year's deprecated API.

<https://nevaberry.com/en/knowledge-patch>

## Install

Claude Code:

```text
/plugin marketplace add Nevaberry/nevaberry-plugins
/plugin install knowledge-patch@nevaberry
/knowledge-patch:knowledge-patch-setup
```

Codex: `codex plugin marketplace add Nevaberry/nevaberry-plugins`, install `knowledge-patch` from `/plugins`, start a new session, then run `$knowledge-patch-setup`.

The plugin is fully offline, works in both CLIs, and needs no credentials. See `plugins/knowledge-patch/README.md` for skills, activation, hooks, and versioning.

Knowledge patches are derived from the respective projects' official release notes and documentation. This project is not affiliated with or endorsed by those projects.
