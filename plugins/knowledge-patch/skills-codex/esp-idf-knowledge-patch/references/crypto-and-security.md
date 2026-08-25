# Cryptography and Security

## Explicit SHA Mode

Since 5.5, `esp_sha_block` and `esp_sha_dma` do not select SHA mode internally.
Select the intended mode before either sub-function API:

```c
esp_sha_set_mode(SHA2_256);
```

## Mbed TLS 4 and PSA Crypto

Mbed TLS 4 removes most legacy `mbedtls_*` cryptographic primitives in favor
of PSA Crypto. Call `psa_crypto_init()` before all cryptographic use, including
certificate parsing and TLS. Normal system startup performs this
initialization, but code running outside that path must do it explicitly.

Hardware-backed ECDSA keys now use `esp_ecdsa_opaque_key_t` and are imported
with `psa_import_key`. RNG callback parameters have disappeared from affected
APIs.

TLS peers must not require any of the following removed or disallowed choices:

- finite-field DHE;
- static ECDH;
- non-forward-secret RSA key exchange;
- curves below 250 bits.

## Crypto Headers and Defaults

Old target AES, SHA, and GCM headers and `sha/sha_{dma,block}.h` are removed.
Use:

- `aes/esp_aes.h`
- `aes/esp_aes_gcm.h`
- `sha/sha_core.h`

ARIA and secp192r1 default off. Pthread-based Mbed TLS threading defaults on.

PSA persistent storage is backed by NVS. Ensure NVS is available and
initialized before using persistent keys.

## Internal Crypto and Secure Boot Renames

In 6.0, replace:

| Old | Current |
| --- | --- |
| `esp_aes_encrypt` / `esp_aes_decrypt` | error-returning `esp_internal_aes_encrypt` / `esp_internal_aes_decrypt` |
| `esp_crypto_shared_gdma_start` | `esp_crypto_shared_gdma_start_axi_ahb` |
| `esp_secure_boot_verify_signature_block` | `esp_secure_boot_verify_ecdsa_signature_block` |

Handle the return status from the internal AES functions rather than treating
them like the removed void-style operations.

## BluFi Protocol Compatibility

BluFi protocol subversion `0x04` requires coordinated client and firmware
updates. Treat it as an end-to-end protocol migration rather than a
firmware-only change.

## NVS Encryption Default

HMAC-based NVS encryption is now the default on supported flash-encrypted
chips. Set `CONFIG_NVS_SEC_KEY_PROTECT_USING_FLASH_ENC=y` to select the former
scheme when compatibility requires it.
