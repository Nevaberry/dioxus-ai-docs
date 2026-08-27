# Networking and protocols

## DNS

### Per-call resolver options (since 28.1)

Option-list variants allow a direct resolver call to override settings without changing shared configuration: `inet_res:gethostbyname/4`, `inet_res:getbyname/4`, and `inet_res:gethostbyaddr/3`.

### TSIG and error atoms (since 28.1)

The internal `inet_dns_tsig` and `inet_res` modules verify the correct TSIG timestamp. Two undocumented DNS error atoms were corrected to the RFC names `notauth` and `notzone`; update code matching the former incorrect atoms.

## TCP and sockets

### Keepalive and user timeout (since 28.3)

`gen_tcp` supports `TCP_KEEPCNT`, `TCP_KEEPIDLE`, and `TCP_KEEPINTVL`. Both `gen_tcp` and `socket` support `TCP_USER_TIMEOUT`.

### Batched datagram operations (since 29.0)

The socket implementation supports `recvmmsg()` and `sendmmsg()` operations for receiving or sending multiple messages per call.

### SCTP peeloff inheritance (since 29.0.1)

An IPv6 SCTP socket returned by peeloff inherits its parent socket's options.

### Accepted-socket option inheritance (since 29.0.2)

The `gen_tcp_socket` accept path inherits options in the same way as classic `gen_tcp`.

### Timeout closure notification (since 29.0.4)

When `send_timeout` and `send_timeout_close` are enabled and a send times out, the socket owner receives the expected `tcp_closed` message.

## HTTP and FTP clients

### Bounded automatic retries (since 28.4)

After a `Retry-After` response, `httpc:request/4,5` retries once by default and then returns the error response instead of retrying indefinitely. `{autoretry, timeout()}` controls this behavior; configure it or implement an application retry policy when more retries are required.

```erlang
HttpOptions = [{autoretry, RetryTimeout}].
```

### Redirect credential boundaries (since 29.0.2)

When `httpc` follows a redirect whose host or port changes, it removes authorization, proxy-authorization, cookie, referer, and origin headers. A client that deliberately forwards credentials must explicitly authorize the new target.

### Passive FTP host validation (since 29.0.2)

FTP clients reject passive-mode replies that redirect the data connection to an arbitrary host.

## SNMP, Diameter, and Megaco

### SNMP USM error responses (since 29.0.1)

`snmpm_usm:generate_outgoing_msg/5` no longer crashes with `badmatch` while building an error response for an unknown user or engine ID.

### Zero-length Diameter AVPs (since 29.0.4)

`diameter_dist:route_session/2` no longer loops indefinitely for a zero-length non-Session-Id AVP or crashes for a zero-length Session-Id AVP with code 263.

### Bounded Megaco property names (since 29.0.4)

The Megaco flex scanner rejects a property parameter name longer than 452 bytes in a text-encoded H.248 message without overflowing its error buffer or crashing the VM.

## Erlang Port Mapper Daemon

### Denial-of-service mitigation (since 29.0.4)

ERTS 17.0.4 mitigates a denial-of-service attack in `epmd`. Release notes classify the change as a potential incompatibility.

### Localhost binding regression fix (since 29.0.5)

ERTS 17.0.5 restores `epmd` localhost binding broken by 29.0.4. Install it when loopback-bound configurations fail after the mitigation. The ERTS application patch can be applied independently to a full OTP 29 installation.
