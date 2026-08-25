# Transports and Operations

Use this reference for transport observability and configuration, structured
logging, broker-specific behavior, TCP limits, and WebSocket customization.

## Microservice Transport Observability

Nest microservice client and server abstractions expose three integration
surfaces:

- `status` observes transport state.
- `on` subscribes to native-driver events.
- `unwrap` provides access to the underlying driver.

Prefer the Nest abstraction for ordinary transport management. Use `on` for
driver events that Nest exposes and `unwrap` only when native-driver access is
actually required.

## Dependency-Injected Microservice Options

Microservice transport options can be resolved through the dependency-injection
container. Use this path when configuration depends on registered providers
instead of constructing every option outside Nest before application startup.

Keep provider availability and initialization order in mind when moving static
transport configuration behind dependency injection.

## Structured Console Logging

`ConsoleLogger` can emit JSON output:

```typescript
const app = await NestFactory.create(AppModule, {
  logger: new ConsoleLogger({ json: true }),
});
```

Use this mode when log collection expects structured records rather than
human-formatted console lines.

## NATS Handler Queues and Shutdown

NATS message handlers can select queues individually. Queue choice no longer has
to be one transporter-wide value for all handlers.

The NATS transporter also provides an optional graceful-shutdown path. Use it
when the server should stop accepting work and complete orderly teardown rather
than immediately close the whole transporter.

## TCP Port and Packet-Buffer Controls

The TCP transporter accepts an operating-system-selected port. This supports
ephemeral-port startup where a fixed port is unnecessary or unavailable.

It also accepts a configurable maximum packet-buffer size. Set an explicit bound
when deployment constraints or untrusted packet streams require limiting how
much incomplete packet data may be buffered.

## RabbitMQ Topic Exchanges

The `11.1.x-selected` guidance adds topic-exchange support to RabbitMQ
microservices. Use a topic exchange when RMQ routing should match topic patterns
rather than relying only on the previously available exchange behaviors.

Keep queue bindings and routing keys consistent with the broker's topic routing
design when enabling this transport feature.

## WebSocket Extension Points

WebSocket errors can retain a cause, allowing the originating failure to remain
attached when an error is wrapped or translated.

The `ws` adapter exposes a message-parser extension point. Use it to parse custom
wire formats before application message handling instead of forcing every
gateway handler to duplicate protocol decoding.

## Expected Framework-Level Exceptions

`IntrinsicException` marks exceptions that Nest should not automatically log.
Use it for expected framework-level failures when automatic logging would create
duplicate or unwanted output; preserve explicit application logging where the
failure still needs an operational record.
