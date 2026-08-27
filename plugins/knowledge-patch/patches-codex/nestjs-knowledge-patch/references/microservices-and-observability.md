# Microservices and Observability

Use this reference when configuring microservice transports, observing their
state, accessing native drivers, handling transport-specific behavior, or
changing logging and exception reporting.

## Transport status, events, and native-driver access

Microservice client and server abstractions expose three transport-facing APIs
(`11.0.0`):

- `status` observes transport state.
- `on` subscribes to native-driver events.
- `unwrap` accesses the underlying driver without leaving the Nest
  abstraction.

Use the narrowest API that fits the task. Reach for `unwrap` only when the
underlying driver itself is needed.

## Dependency-injected transport options

Microservice configuration can be resolved through the dependency-injection
container (`11.0.0`). Transport options may therefore depend on registered
providers instead of being built entirely outside Nest.

## NATS handler queues and shutdown

NATS message handlers can choose queues individually (`11.0.0`). Queue choice
does not need to apply as one setting to every handler on the server.

The NATS transporter also provides an optional graceful-shutdown path. Use it
when teardown should be graceful rather than immediate.

## TCP transport bounds and ephemeral ports

The TCP transporter accepts an operating-system-selected port (`11.0.0`),
which permits ephemeral-port startup. It also accepts a configurable maximum
packet-buffer size, providing an explicit bound on buffered packets.

## RabbitMQ topic exchanges

RabbitMQ microservices support topic exchanges (`11.1.x-selected`). This lets
applications use topic-based routing through Nest's RMQ transport.

## Structured JSON console logging

`ConsoleLogger` can emit structured JSON (`11.0.0`). Enable it through the
logger passed to `NestFactory.create`.

```typescript
const app = await NestFactory.create(AppModule, {
  logger: new ConsoleLogger({ json: true }),
});
```

## Intrinsic exceptions

`IntrinsicException` marks exceptions that Nest should not log automatically
(`11.0.0`). Use it for expected framework-level failures when automatic
logging would duplicate or otherwise produce unwanted output.

