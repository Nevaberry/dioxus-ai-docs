# nevaberry-plugins

Public plugin marketplace for the `knowledge-patch` plugin: one dual-format Claude Code / Codex plugin shipping versioned technology knowledge patches as native skills.

## Public Repository Notice

THIS REPO IS PUBLIC.

Future contributors and AI agents: never commit anything sensitive, private, local-machine-specific, or questionable to this repository. That includes absolute home paths, hostnames, emails, keys, credentials, internal repository names, private notes, or generated material that has not been reviewed for public release.

## Knowledge Patch Plugin

See `plugins/knowledge-patch/README.md` for plugin layout, commands, hooks, and activation details.

This repository also ships a Codex marketplace manifest at `.agents/plugins/marketplace.json` for Codex's plugin installer.

Knowledge patches are derived from the respective projects' official release notes and documentation. This project is not affiliated with or endorsed by those projects.

## Install

Add the marketplace in Claude Code:

```text
/plugin marketplace add Nevaberry/nevaberry-plugins
```

Install the plugin:

```text
/plugin install knowledge-patch@nevaberry
```

Reload plugins:

```text
/reload-plugins
```

Then invoke the native setup skill:

```text
/knowledge-patch:knowledge-patch-setup
```

You can also ask Claude Code to set up Knowledge Patch in natural language. The shorter `/knowledge-patch:setup` command remains a compatibility alias.

## Install with Codex

Add the marketplace from the Codex CLI:

```text
codex plugin marketplace add Nevaberry/nevaberry-plugins
```

Open `/plugins`, choose **Nevaberry**, install `knowledge-patch`, and start a new session. In the IDE extension, use **Settings > Plugins** and start a new chat after installation.

Then invoke `$knowledge-patch-setup` or ask Codex to set up Knowledge Patch for the current project. The plugin is fully offline and does not require service credentials.
