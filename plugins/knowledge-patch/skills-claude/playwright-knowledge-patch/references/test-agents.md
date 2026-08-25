# Built-in Test Agents

## Generate client definitions

Playwright ships planner, generator, and healer definitions. Generate the set
for the consuming client loop:

```bash
npx playwright init-agents --loop=vscode
```

Choose the corresponding supported loop for VS Code, OpenCode, or another
supported client integration. The VS Code loop requires VS Code 1.105 or newer.
Regenerate definitions after every Playwright upgrade so their instructions and
MCP tools stay synchronized with the installed release.

## Planner

The planner explores the live application and writes a Markdown plan under
`specs/`. It starts from a seed test so application state and project-specific
setup are ready before exploration.

## Generator

The generator turns a plan into executable tests under `tests/`. It verifies
selectors and assertions against the application instead of merely copying
planned text.

## Healer

The healer replays a failure, proposes repairs to locators, waits, or data, and
reruns until the test passes or its guardrails stop it. It may skip a test when
the application's behavior itself appears broken.

## Seed tests and audit links

A planner seed test supplies the ready-to-use page, fixtures, hooks, global
setup, and project dependencies. It also serves as the style template for
generated tests. Generated test comments can link each test back to its source
plan and seed, preserving the artifact trail from `specs/` to `tests/`.
