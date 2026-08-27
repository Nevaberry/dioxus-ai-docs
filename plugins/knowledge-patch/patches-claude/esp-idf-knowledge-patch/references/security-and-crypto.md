# Security and Cryptography

## Explicit SHA mode (5.5)

`esp_sha_block` and `esp_sha_dma` no longer select the SHA mode themselves.
Select it before calling either sub-function API:

```c
esp_sha_set_mode(SHA2_256);
```

## ESP-TLS stack integration (6.0)

Built-in wolfSSL support and its Kconfig options are removed. Standard
applications can use the default mbedTLS stack. To provide another TLS stack:

1. Enable `CONFIG_ESP_TLS_CUSTOM_STACK`.
2. Implement `esp_tls_stack_ops_t`.
3. Call `esp_tls_register_stack` before opening a connection.

`esp_tls_conn_http_new` is removed. Allocate a context with `esp_tls_init` and
call the appropriate `_sync` or `_async` connection replacement.

## Mbed TLS 4 and PSA Crypto (6.0)

Mbed TLS 4 removes most legacy `mbedtls_*` cryptographic primitives in favor of
PSA Crypto. Call `psa_crypto_init()` before all cryptographic use, including
certificate parsing and TLS. Normal system startup initializes it, but direct
use outside that startup path must initialize explicitly.

Hardware-backed ECDSA keys use `esp_ecdsa_opaque_key_t` and are imported with
`psa_import_key`. RNG callback parameters disappear from affected APIs. TLS
peers must not require finite-field DHE, static ECDH, non-forward-secret RSA
key exchange, or curves smaller than 250 bits.

### Header and default changes

| Removed header | Replacement |
| --- | --- |
| old target AES headers | `aes/esp_aes.h` |
| old target GCM headers | `aes/esp_aes_gcm.h` |
| old target SHA and `sha/sha_{dma,block}.h` | `sha/sha_core.h` |

ARIA and secp192r1 default off. Pthread-backed Mbed TLS threading defaults on.
PSA persistent storage is backed by NVS, so initialize NVS and keep it
available before using persistent keys.

## Low-level crypto replacements (6.0)

- Replace `esp_aes_encrypt` and `esp_aes_decrypt` with the error-returning
  `esp_internal_aes_encrypt` and `esp_internal_aes_decrypt`; handle failures.
- Replace `esp_crypto_shared_gdma_start` with
  `esp_crypto_shared_gdma_start_axi_ahb`.
- Replace `esp_secure_boot_verify_signature_block` with
  `esp_secure_boot_verify_ecdsa_signature_block`.

BluFi protocol subversion `0x04` requires coordinated client and firmware
updates. Do not update only one side.

HMAC-based NVS encryption is the default on supported flash-encrypted chips.
Set `CONFIG_NVS_SEC_KEY_PROTECT_USING_FLASH_ENC=y` to select the former
flash-encryption-based key-protection scheme.
