# Networking and Services

## Configure TCP and socket behavior

### Keepalive and user-timeout options

Since 28.3, `gen_tcp` supports `TCP_KEEPCNT`, `TCP_KEEPIDLE`, and
`TCP_KEEPINTVL`. Both `gen_tcp` and `socket` support `TCP_USER_TIMEOUT`.
Account for operating-system support and units when setting the options.

### Batched datagram operations

Since 29.0, the `socket` implementation supports `recvmmsg()` and
`sendmmsg()` to receive or send multiple messages in one call.

### Inherited accepted-socket options

Since 29.0.2, the `gen_tcp_socket` accept path inherits options in the same way
as classic `gen_tcp`. Remove workarounds that assumed accepted sockets lost
those settings, but keep explicit configuration where ownership or subsequent
changes require it.

Since 29.0.1, an IPv6 SCTP socket returned by peeloff inherits its parent
socket's options.

### Timeout close notifications

Since 29.0.4, when `send_timeout` and `send_timeout_close` are both enabled and
a send times out, the socket owner receives the expected `tcp_closed` message.
Handle both the send failure and the asynchronous closure notification.

## Resolve DNS per request

Since 28.1, these direct-resolver variants accept an option list so one call
can override resolver settings without changing shared configuration:

- `inet_res:gethostbyname/4`
- `inet_res:getbyname/4`
- `inet_res:gethostbyaddr/3`

The internal `inet_dns_tsig` and `inet_res` modules also verify the correct
TSIG timestamp. Two undocumented DNS error atoms were corrected to the RFC
names `notauth` and `notzone`; update code that matched the former atoms.

## Bound HTTP retry behavior

Since 28.4, `httpc:request/4,5` retries once by default after a `Retry-After`
response and then returns the error response instead of retrying forever.
Control the behavior with the HTTP option `{autoretry, timeout()}`:

```erlang
HttpOptions = [{autoretry, RetryTimeout}].
```

Applications needing unbounded retries must configure the option or own the
retry loop, including its cancellation and overall deadline.

Since 29.0.2, a redirect that changes host or port strips `authorization`,
`proxy-authorization`, `cookie`, `referer`, and `origin` headers. A client that
intentionally forwards credentials across that boundary must authorize the new
target explicitly.

## Configure SSH services explicitly

### Daemon services

Since 29.0, `ssh:daemon/2` does not enable shell, exec, or SFTP services by
default. Opt in to the required services:

```erlang
ssh:daemon(Port, [
    {shell, {shell, start, []}},
    {exec, erlang_eval},
    {subsystems, [ssh_sftpd:subsystem_spec([])]}
    | Options
]).
```

### Hybrid key exchange

Since 28.4, SSH supports `mlkem768x25519-sha256`. Since 29.0 it is the first
preferred key exchange, with fallback for peers lacking support.

Since 29.0.4, every Diffie-Hellman path checks `1 < e/f < p-1` and
`1 < K < p-1`. For DH-GEX, clients reject `P` values smaller than 2048 bits or
`G` outside `(1, P-1)`, and `dh_gex_limits` defaults to a 2048-bit minimum on
clients and servers.

### Compatibility and packet validation

Since 29.0.3, SSH no longer applies the obsolete SHA-1 authentication
workaround for OpenSSH 7.x. Retest legacy integrations that depended on it.

In 29.0.5, `ssh` 6.0.4 rejects incoming packets that are not aligned to the
cipher block size. CBC connections use a timing-safe discard path before
disconnecting, so structural errors cannot be distinguished from MAC failures.
AEAD and encrypt-then-MAC connections disconnect immediately. The SSH
application patch can be applied independently to a full OTP 29 installation.

## Confine file-transfer services

Since 29.0.2:

- FTP clients reject passive responses that redirect the data connection to an
  arbitrary host; and
- SFTP `READLINK` keeps paths relative to the configured root and does not
  reveal host paths outside it.

Since 29.0.3, SFTP `REALPATH` requests containing `..` no longer reveal whether
paths outside the configured root exist. The SFTP server also caps a read
request at 255 KiB, so clients must split larger reads.

The `ftp` and `ct_ftp` modules were deprecated in 29.0 and are scheduled for
removal in OTP 30. Plan a replacement rather than building new dependencies on
them.

## Enforce TLS distribution boundaries

Since 29.0.2, Erlang distribution over TLS applies the same-LAN restriction
when `check_ip` is enabled. A node connection accepted by an earlier patch can
therefore be rejected. Verify the intended LAN boundary and certificates
during rollout.

## Operate `epmd` across security patches

ERTS 17.0.4 in OTP 29.0.4 mitigates a denial-of-service attack in `epmd`; its
release note classifies the change as a potential incompatibility.

ERTS 17.0.5 in OTP 29.0.5 fixes the resulting regression that prevented
`epmd` from binding to localhost. Install it when loopback-bound
configurations fail after 29.0.4. The ERTS application patch can be applied
independently to a full OTP 29 installation.

## Handle protocol edge cases

### Diameter

Since 29.0.4, `diameter_dist:route_session/2` no longer loops forever on a
zero-length non-Session-Id AVP or crashes on a zero-length Session-Id AVP
(code 263).

### Megaco

Since 29.0.4, the Megaco flex scanner bounds property parameter names in
text-encoded H.248 messages. Names longer than 452 bytes no longer overflow
the error buffer and crash the VM.

### SNMP

Since 29.0.1, `snmpm_usm:generate_outgoing_msg/5` no longer crashes with
`badmatch` while building an error response for an unknown user or engine ID.
