# NTRIP and Correction Routing

## AgIO client controls

AgIO 6.8.5 separates caster requests, receiver-position feedback, and
correction output routes.

For the caster request, AgIO can issue the mountpoint `GET` using an HTTP/1.0
or HTTP/1.1 form and optional Basic authorization. Use **Verify** to test
reachability. Use **Get Source Table** to discover the actual mountpoint rather
than relying on a guessed name.

GGA feedback can use either a fixed position or the live receiver position.
An interval of `0` disables GGA transmission.

Received RTCM can leave AgIO through:

- a selected serial output;
- UDP, usually port `2233` for All-In-One Teensy hardware.

Alternatively, **Serial NTRIP** accepts corrections locally for onward
routing. Do not confuse that inbound local path with AgIO's own caster request.

## Evidence at each layer

Treat the following as independent checks:

1. The host can reach the caster.
2. Authentication and mountpoint selection succeed.
3. Correction bytes arrive and remain fresh.
4. AgIO sends them over the selected output.
5. The receiver consumes them.

A successful **Verify** result or open connection does not establish all five.

## AgOpen Ntripcaster deployment

AgOpen Ntripcaster is a separate caster application built with ASP.NET,
React/TypeScript, and PostgreSQL. It provides mountpoint and access management
and a conventional NTRIP listener on port `2101`.

The source snapshot has no published release line. Pin a commit or deployment
image, and test source-upload compatibility explicitly: its example uses the
legacy `SOURCE` request syntax.
