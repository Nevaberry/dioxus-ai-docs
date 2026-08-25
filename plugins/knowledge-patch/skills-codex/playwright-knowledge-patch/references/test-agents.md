# Built-in Test Agents

## Initialize the agent loop

The `mcp-and-test-agents` guidance includes planner, generator, and healer
agent definitions. Generate definitions for a supported loop with:

```sh
npx playwright init-agents --loop=vscode
npx playwright init-agents --loop=claude
npx playwright init-agents --loop=opencode
```

Regenerate the definitions after Playwright upgrades so their instructions and
MCP tools remain current. The VS Code loop requires VS Code 1.105 or newer.

## Planner

The planner explores the application and writes a Markdown plan.

## Generator

The generator verifies selectors and assertions while converting the plan into
executable tests.

## Healer

The healer replays failures, proposes repairs, and reruns until the test passes
or guardrails stop it. It may skip a test when the application behavior itself
appears broken.

## Seed tests

A planner seed test supplies:

- the ready-to-use page;
- fixtures and hooks;
- global setup;
- project dependencies;
- the style template for generated tests.

## Generated artifacts

Plans are stored under `specs/`, while executable tests are stored under
`tests/`. Generated test comments can link each test to its source plan and
seed.
