# Features and Release Policy

## Fully secure core release policy

The release index marks WooCommerce 11.0.1, released on 2026-08-10, as stable
and says only the latest core version is considered fully secure. Treat
downloadable legacy point releases as packages, not as evidence of a fully
secure supported branch.

## Core cost of goods sold and MCP beta

WooCommerce 10.3.0 is the release where cost of goods sold came to core and
MCP entered beta. Use 10.3.0 as the compatibility boundary for integrations
that depend on those capabilities.

## Interactivity API Mini-Cart

WooCommerce 10.4.0 is the release where the Interactivity API Mini-Cart went
live. Test theme and extension compatibility for that Mini-Cart implementation
against 10.4.0 or newer.

## Email previews

WooCommerce 9.8.0 introduced email previews alongside modernized designs. Use
9.8.0 as the minimum release when relying on the preview workflow.
