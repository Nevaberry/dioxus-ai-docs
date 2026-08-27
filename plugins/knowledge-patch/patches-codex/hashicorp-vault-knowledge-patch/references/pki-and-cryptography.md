# PKI and Cryptography

Use this reference for Transit, PKI, ACME, SCEP, KMIP, managed keys, TLS, and
cryptographic compatibility.

## Transit and key operations

### Transit cryptography additions (`1.19-changelog`)

Transit adds experimental ML-DSA signatures, Enterprise Ed25519ph and
Ed25519ctx signing/verification, and RSA encryption with `pkcs1v15` padding.
Stored ML-DSA and SLH-DSA keys remain usable after policy reloads in later
fixes.

### Additional Transit algorithms (`1.20-changelog`)

Transit adds experimental SLH-DSA signatures. Enterprise also supports 192-bit
AES CMAC keys.

### Transit additions (`1.21-changelog`)

Enterprise Transit supports AES-CBC encryption/decryption, `context` on
datakeys and derived-key endpoints for derived DEKs, and managed keys on the
rewrap endpoint.

### MSSQL EKM Transit key-version control (`1.21`)

The MSSQL EKM provider lets an administrator choose the Transit key versions
used to wrap and unwrap SQL Server data-encryption keys, including during
encrypted-backup restoration.

### Managed-key usage response (`2.0-changelog`)

`GET sys/managed-keys/:type/:name` returns usage names rather than numeric IDs:
`encrypt`, `decrypt`, `sign`, `verify`, `wrap`, `unwrap`, `generate_random`, and
`mac`. Update consumers that decode integers.

### Random-byte APIs (`2.0-changelog`)

Core and Transit random-byte endpoints permit larger results and pseudorandom
bytes seeded from random sources. Large requests use proportionally more
memory.

### Multi-region AWS KMS keys (`2.0-changelog`)

The Enterprise key-management secrets engine supports multi-region AWS KMS
keys.

### Transit envelope encryption (`2.0`)

Transit can protect data-encryption keys while applications encrypt and decrypt
bulk data locally.

### PKCS#11 managed-key token selection (`2.0.4`)

Enterprise PKCS#11 managed keys make `slot` and `token_label` strictly mutually
exclusive and accept slot values wider than 32 bits. To change addressing
mode, clear the old identifier in the same request:

```json
{"slot":"","token_label":"hsm-token"}
```

### Managed-key Transit certificate operations (`2.0.4`)

Enterprise Transit accepts managed keys on CSR-signing and certificate-chain
setting endpoints.

## Cryptographic runtime constraints

### FIPS and TLS cryptography (`1.19-changelog`)

FIPS builds use a FIPS 140-3 module and compliant algorithms. Go TLS supports
X25519MLKEM768 hybrid post-quantum key agreement.

### Asymmetric key-size bounds (`1.19-changelog`)

Enterprise KMIP RSA generation requires at least 2048 bits. From 1.19.18, SSH
secrets-engine RSA keys are capped at 8192 bits.

### Password-generation entropy (`1.21-changelog`)

Enterprise password-generation policies can choose an entropy source,
including `seal` for entropy augmentation.

### Common Criteria mode (`2.0-changelog`)

Enterprise `common_criteria_mode` restricts listener TLS cipher suites. PKI
validates full chains, can enforce validation-time checks, treats `NotBefore`
as zero, enforces minimum key usages for extended-key-usage sets, and rejects
uploaded certificates without a trust chain.

## PKI issuance, chains, and revocation

### PKI issuer constraints and chains (`1.19-changelog`)

PKI enforces issuer extended-key-usage, name-constraint, and issuer-name
extensions for leaf issuance/signing. A signing CA's `max_path_length` limits
`root/sign-intermediate`. Unusable issuers reject manual chains; Enterprise
issuer fields can disable selected chain validations.

### PKI expiry and subject controls (`1.19-changelog`)

`leaf_not_after_behavior = "always_enforce_err"` rejects overlong TTLs for CA
issuance and ACME as well as leaves. Roles support `serial_number_source`, and
issuance honors maximum TTL.

### PKI names and protocol usages (`1.19-changelog`)

Root/intermediate creation supports remaining permitted/excluded email, IP,
URI, and DNS name constraints. Role `alt_names` accepts glob DNS names. SCEP,
EST, and CMPv2 can issue without the `server_flag` key usage.

### PKI CRL guardrail (`1.19-changelog`)

Set `max_crl_entries` to keep a runaway revocation list from overloading Vault.

### Delta CRL distribution points (`1.20-changelog`)

Mount- and issuer-level AIA can advertise Freshest CRLs, and base CRLs carry
the Freshest CRL extension.

### PKI response and integration APIs (`1.21-changelog`)

PKI issue, sign, and fetch responses include `AuthorityKeyID`. Enterprise adds
`batch/certs` for fetching certificates in bulk and `integrations/guardium`
configuration.

### PKI CSR constraints (`1.21-changelog`)

`sign-verbatim` copies a CSR basic-constraints extension when `isCA=false` and
rejects it when `isCA=true`.

### PKI token-display-name role constraint (`upgrade-safety`)

`allow_token_displayname` is deprecated and targeted for removal in April
2027. Replace it with `allowed_domains`, `allow_bare_domains`,
`allow_subdomains`, or `allow_glob_domains` constraints.

## ACME, SCEP, External CA, and KMIP

### ACME validation and administration (`1.19-changelog`)

Use `challenge_permitted_ip_ranges` and `challenge_excluded_ip_ranges` to
control HTTP-01 and TLS-ALPN-01 validation destinations. APIs can list account
key IDs, read account/order/certificate details, and update account status.
Validation failures return ACME-specific error types.

### PKI SCEP server (`1.20-changelog`)

Enterprise PKI provides SCEP for non-Vault-API clients. It can use an issuer
backed by an RSA PKCS#11 managed key.

### Managed-key SSH signing (`1.20-changelog`)

The Enterprise SSH secrets engine can sign SSH keys with managed keys.

### SCEP role and capability enforcement (`1.21-changelog`)

Enterprise SCEP roles enforce `token_bound_cidrs`. `GetCACaps` reflects chosen
encryption and digest algorithms and advertises `POSTPKIOperation`.

### PKI External CA and Agent ACME (`2.0-changelog`)

The Enterprise External CA plugin obtains public-CA certificates through ACME.
Vault Agent runs those ACME flows natively, and templates re-render when an
External CA certificate is issued or renewed.

### KMIP CA and request APIs (`2.0-changelog`)

KMIP APIs manage multiple client-verification CAs and import external CAs.
Enterprise also has an experimental KMIP-request execution API.

### External CA PEM bundle contents (`2.0.4`)

For Enterprise External CA responses with `certificate_format=pem_bundle`, the
`certificate` field now includes the private key. Treat it as sensitive and
parse the extra PEM block.
