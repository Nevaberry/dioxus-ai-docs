# Built-in Test Agents

## Generate current definitions

Initialize the three bundled test agents with the loop matching the consuming client:

```bash
npx playwright init-agents --loop=vscode
```

The command generates static definitions. Regenerate them after every Playwright upgrade so their instructions and MCP tools match the installed release.

## Planner, generator, and healer

The workflow splits responsibility among three roles:

1. The planner explores the live application and writes a human-readable Markdown plan under `specs/`.
2. The generator consumes that plan, verifies locators and assertions against the live application, and writes Playwright tests under `tests/`.
3. The healer runs a failing test, replays its steps, repairs locators, waits, or data, and reruns until the test passes or guardrails stop it.

If the healer determines that product behavior itself is broken, it can skip the test instead of forcing an artificial passing repair.

## Seed tests

A seed test provides a ready-to-use page and project-specific fixtures. It also serves as the style example for generated tests.

```ts
// tests/seed.spec.ts
import { test } from './fixtures';

test('seed', async ({ page }) => {
  // Establish the application state used for planning and generation.
});
```

Before exploring, the planner runs the seed with global setup, project dependencies, hooks, and fixtures. A plan can begin from the seed or from scratch and can also receive a product-requirements document.

## Plans and generated suites

- Plans are stored in `specs/*.md`.
- Generated suites are stored in `tests/`.
- Generated tests align one-to-one with specs where feasible.
- Generated files retain comments that link each test to its source spec and seed test, preserving an auditable path from intent and setup to implementation.
