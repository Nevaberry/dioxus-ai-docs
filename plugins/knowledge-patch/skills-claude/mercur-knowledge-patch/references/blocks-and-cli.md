# Blocks and CLI

## Official registry blocks (2.0.0)

The official registry names are:

- `reviews`;
- `product-import-export`;
- `team-management`;
- `wishlist`;
- `vendor-notifications`;
- `algolia`;
- `requests`; and
- `vendor-chat`.

Each block may install its backend, API, and panel-extension pieces together.

## CLI lifecycle (2.0.0)

`@mercurjs/cli` manages:

- project creation;
- registry discovery;
- block installation and comparison;
- route type generation; and
- custom registry builds.

The available commands shown for these workflows are:

```bash
bunx @mercurjs/cli create my-marketplace
mercurjs init
mercurjs search -q "payment"
mercurjs view reviews
mercurjs add reviews wishlist vendor-chat
mercurjs diff reviews
mercurjs codegen
mercurjs build
```

## Project templates (2.0.0)

The available templates are:

| Template | Purpose |
| --- | --- |
| `basic` | A marketplace with both panels |
| `registry` | Distribution of blocks |
| `plugin` | Reusable Medusa plugins |
