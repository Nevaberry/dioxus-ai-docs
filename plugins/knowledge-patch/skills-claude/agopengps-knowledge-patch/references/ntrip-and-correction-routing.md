# NTRIP and Correction Routing

## AgIO client controls

In 6.8.5, AgIO can issue a mountpoint `GET` using either HTTP/1.0 or HTTP/1.1
form and optional Basic authorization. **Verify** checks reachability;
**Get Source Table** discovers the actual mountpoint. Use those operations for
their distinct purposes rather than treating a successful reachability test as
proof that a configured mountpoint exists.

GGA can use a fixed position or the live position. An interval of `0` disables
GGA transmission.

Received RTCM corrections can leave AgIO through:

- serial output;
- UDP, commonly port `2233` for All-In-One Teensy hardware; or
- local input through **Serial NTRIP**, followed by onward routing.

Verify the selected correction route as a separate stage from caster login and
correction reception.

## AgOpen Ntripcaster deployment identity

AgOpen Ntripcaster is a separate ASP.NET, React/TypeScript, and PostgreSQL caster
with mountpoint and access management. Its conventional NTRIP listener is port
`2101`.

There is no published release line in this snapshot. Pin a deployment to an
exact commit or image and test source-upload compatibility. In particular, its
example uses legacy `SOURCE` syntax, so do not assume every source uploader uses
the same request form.

