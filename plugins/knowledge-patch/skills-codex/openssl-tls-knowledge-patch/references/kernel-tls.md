# Linux Kernel TLS

## Contents

- [Transmit record construction](#transmit-record-construction)
- [Receive semantics and errors](#receive-semantics-and-errors)
- [Non-application record types](#non-application-record-types)
- [TLS 1.3 key updates](#tls-13-key-updates)
- [Zero-copy and receive optimizations](#zero-copy-and-receive-optimizations)
- [Record-size limits](#record-size-limits)
- [Observability](#observability)

## Transmit record construction

### Preserve record boundaries with `MSG_MORE`

After installing `TLS_TX`, each `send()` ends a TLS record unless it passes `MSG_MORE`. Data accumulated by calls with `MSG_MORE` is emitted when a later call omits the flag or the maximum record size is reached. `sendfile()` uses records of up to 2^14 bytes.

The kernel reserves the encrypted output buffer during `send()`. If allocation cannot proceed, the call blocks for memory or fails wholly with `ENOMEM`; it does not partially accept that call's data. Data queued by an earlier `MSG_MORE` call remains queued after the failure.

## Receive semantics and errors

### Wait for complete records

`TLS_RX` waits for a complete record before decrypting. If the destination buffer is smaller than the record, the kernel decrypts into a kernel buffer and copies out the requested part rather than treating the buffer size as a protocol error.

### Distinguish receive failures

- `EINVAL` means the record's TLS version differs from the configured version.
- `EMSGSIZE` means the record is oversized.
- `EBADMSG` covers other decryption failures.

Use these codes to separate configuration mismatch, record framing, and authentication failures.

## Non-application record types

### Send record types through ancillary data

Send a non-application record as plaintext through `sendmsg()` and attach a one-byte record type using a `SOL_TLS` / `TLS_SET_RECORD_TYPE` control message. The kernel encrypts the payload.

```c
cmsg->cmsg_level = SOL_TLS;
cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
cmsg->cmsg_len = CMSG_LEN(sizeof(unsigned char));
*(unsigned char *)CMSG_DATA(cmsg) = 21; /* alert */
```

### Receive record types through ancillary data

`recvmsg()` reports the type through `SOL_TLS` / `TLS_GET_RECORD_TYPE` and never combines different record types in one return. Supply a control buffer whenever a control record can arrive. Application-data records can still be read without a control buffer.

## TLS 1.3 key updates

### Hand new traffic keys to the kernel

Install new TLS 1.3 traffic keys by applying `TLS_TX` or `TLS_RX` again without changing the configured version or cipher.

After receiving KeyUpdate, the kernel pauses decryption until userspace installs the new RX key. Intervening reads fail with `EKEYEXPIRED`, and `poll()` does not report a read event. TX is not paused. Prevent key or nonce reuse in userspace because the kernel does not detect it.

## Zero-copy and receive optimizations

### Keep zero-copy source data immutable

`TLS_TX_ZEROCOPY_RO` lets device-offloaded `sendfile()` data reach the NIC without an in-kernel copy. Keep submitted bytes unchanged until transmission completes. Mutation can make the original transmission differ from a retransmission and cause the peer to reject record authentication.

### Enable no-padding receive only for trusted peers

For TLS 1.3, `TLS_RX_EXPECT_NO_PAD` allows direct decryption into userspace when the sender is expected not to pad records. Enable it only for a trusted peer. A padded or non-data record must be decrypted again into a kernel buffer, doubling work. Retries increment `TlsDecryptRetry`; data-record violations also increment `TlsRxNoPadViolation`.

## Record-size limits

### Set the outgoing plaintext cap correctly

`TLS_TX_MAX_PAYLOAD_LEN` caps every outgoing plaintext fragment and can implement the TLS Record Size Limit extension.

- For TLS 1.2, set it to the negotiated record-size limit; valid values are 64–16384.
- For TLS 1.3, set it to `record_size_limit - 1` because the negotiated limit includes the ContentType byte; valid values are 63–16384.

## Observability

### Inspect socket and namespace state

Read per-socket optimization state through `getsockopt()` and socket diagnostics such as `ss`. Read per-network-namespace counters from `/proc/net/tls_stat`.

The counters distinguish current and cumulative software and device sessions, decryption failures and retries, device RX resynchronizations, successful and failed TX/RX rekeys, and received KeyUpdate messages that require a new RX key.
