# Platforms, devices, and reporting

## App Marketplace eligibility

Since March 27, 2025, an application needs at least five active Square sellers
before it is eligible for Square App Marketplace listing.

## GraphQL Labor and device entry points

Square GraphQL provides `scheduledShifts` and `timecards` for Labor data, with
`timecards` replacing deprecated `shifts`.

It also provides `devices` for retrieving a seller's POS and peripheral
devices.

## Devices API hardware details

Devices API adds `DeviceType.HANDHELD` for Square Handheld and a `mac_address`
field to both `WifiDetails` and `EthernetDetails`.

## Square MCP server

Square provides an MCP server through which compatible AI assistants can
control and interact with a Square account.

## Customer bank accounts

The Bank Accounts API provides `CreateBankAccount` to store a new customer bank
account and `DisableBankAccount` to disable one.

## JWT OAuth access tokens

The OAuth API adds a `use_jwt` parameter for authenticating with a JSON Web
Token. It behaves like a standard access token.

## Reporting API

The Beta, cube-based Reporting API uses `GET /v1/meta` to discover views,
cubes, measures, dimensions, and segments. Use `POST /v1/load` to run
analytical queries. The API supports automatic joins across cubes.

Authenticate with a personal access token or an OAuth token carrying
`REPORTING_READ`.
