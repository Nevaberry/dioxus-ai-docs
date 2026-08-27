# Blocks and CLI

## Official registry blocks (2.0.0)

The official registry names are:

- `reviews`
- `product-import-export`
- `team-management`
- `wishlist`
- `vendor-notifications`
- `algolia`
- `requests`
- `vendor-chat`

Each block may install backend, API, and panel-extension pieces together.

## CLI lifecycle (2.0.0)

`@mercurjs/cli` manages project creation, registry discovery, block installation and
comparison, route type generation, and custom registry builds.

Create a marketplace:

```bash
bunx @mercurjs/cli create my-marketplace
```

Initialize Mercur in a project:

```bash
mercurjs init
```

Search the registry and inspect a block:

```bash
mercurjs search -q "payment"
mercurjs view reviews
```

Install one or more blocks and compare a local block with its registry source:

```bash
mercurjs add reviews wishlist vendor-chat
mercurjs diff reviews
```

Generate route types and build a custom registry:

```bash
mercurjs codegen
mercurjs build
```

## Project templates (2.0.0)

The available templates are:

- `basic`: a marketplace with both panels;
- `registry`: a project for distributing blocks;
- `plugin`: a reusable Medusa plugin.
