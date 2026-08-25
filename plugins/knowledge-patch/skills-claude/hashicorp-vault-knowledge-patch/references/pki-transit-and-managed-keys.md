# PKI, Transit, and Managed Keys

## PKI issuer and leaf constraints

### Issuer chains and extensions

PKI enforces issuer extended-key-usage, name-constraint, and issuer-name
extensions while issuing or signing leaves. A signing CA's `max_path_length`
limits `root/sign-intermediate`; unusable issuers reject manual chains.
Enterprise issuer fields can disable selected chain validations.
(`1.19-changelog`)

Root and intermediate creation accepts permitted and excluded email, IP, URI,
and DNS name constraints. Role `alt_names` accepts glob-style DNS names.
(`1.19-changelog`)

### Lifetime and subject controls

`leaf_not_after_behavior = "always_enforce_err"` rejects an overlong TTL for
normal issuance, CA issuance, and ACME. Roles accept `serial_number_source`, and
issuance observes the configured maximum TTL. (`1.19-changelog`)

The legacy role field `allow_token_displayname` is deprecated and targeted for
removal in April 2027. Replace it with constraints such as `allowed_domains`,
`allow_bare_domains`, `allow_subdomains`, or `allow_glob_domains`.
(`upgrade-safety`)

### CSR and response details

PKI issue, sign, and fetch responses include the certificate
`AuthorityKeyID`. Enterprise adds `batch/certs` for fetching multiple
certificates and `integrations/guardium` for integration configuration.
(`1.21-changelog`)

`sign-verbatim` copies a CSR basic-constraints extension when `isCA=false` and
rejects that extension when `isCA=true`. (`1.21-changelog`)

## Revocation and distribution

Set `max_crl_entries` to keep a runaway revocation list from overloading Vault.
(`1.19-changelog`)

Mount- and issuer-level AIA can advertise Freshest CRLs, and base CRLs include
the Freshest CRL extension. (`1.20-changelog`)

## ACME, SCEP, EST, and CMPv2

### ACME validation and administration

`challenge_permitted_ip_ranges` and `challenge_excluded_ip_ranges` constrain
HTTP-01 and TLS-ALPN-01 validation targets. APIs can list account key IDs,
retrieve account, order, and certificate details, and update account status.
Validation failures return ACME-specific error types. (`1.19-changelog`)

### SCEP and other enrollment protocols

SCEP, EST, and CMPv2 can issue certificates without the `server_flag` key
usage. (`1.19-changelog`)

Enterprise PKI exposes a SCEP server for non-Vault API clients, including use
of an issuer backed by an RSA PKCS#11 managed key. (`1.20-changelog`)

Enterprise SCEP roles enforce `token_bound_cidrs`. `GetCACaps` reflects the
configured encryption and digest algorithms and advertises
`POSTPKIOperation`. (`1.21-changelog`)

### External CA and Vault Agent

The Enterprise External CA plugin obtains public-CA certificates through ACME,
and Vault Agent can execute those ACME workflows. Agent templates re-render
when the external-CA certificate is issued or renewed. (`2.0-changelog`)

For `certificate_format=pem_bundle`, an External CA response includes the
private key inside the `certificate` field. Treat that field as secret and
expect the extra PEM block when parsing. (`2.0.4`)

## Transit algorithms and workflows

### Signatures, encryption, and MAC

Transit adds experimental ML-DSA signatures and Enterprise Ed25519ph and
Ed25519ctx signing and verification. RSA encryption accepts `pkcs1v15` padding.
Later fixes keep stored ML-DSA and SLH-DSA keys usable after policy reload.
(`1.19-changelog`)

Transit adds experimental SLH-DSA signatures. Enterprise Transit supports
192-bit AES CMAC keys. (`1.20-changelog`)

Enterprise Transit supports AES-CBC encryption and decryption. `context` on
datakey and derived-key endpoints encrypts derived DEKs, and rewrap supports
managed keys. (`1.21-changelog`)

Transit envelope encryption lets applications encrypt bulk data locally while
Vault protects the data-encryption keys. (`2.0`)

### Random bytes and entropy

Core and Transit random-byte APIs accept larger responses and can return
pseudorandom bytes seeded from random sources. Large responses use
correspondingly more memory. (`2.0-changelog`)

Enterprise password-generation policies can select an entropy source,
including `seal` for entropy augmentation. (`1.21-changelog`)

## Managed keys and external key managers

### Algorithms, sizing, and cloud identity

Enterprise KMIP RSA key generation enforces a 2048-bit minimum. SSH secrets
keys are capped at 8192 RSA bits from 1.19.18. (`1.19-changelog`)

Enterprise GCP managed keys can use workload identity federation credentials.
(`1.19-changelog`)

The Enterprise SSH secrets engine can use managed keys to sign SSH keys.
(`1.20-changelog`)

The Enterprise key-management secrets engine supports multi-region AWS KMS
keys. (`2.0-changelog`)

### PKCS#11 addressing

Enterprise PKCS#11 managed keys treat `slot` and `token_label` as mutually
exclusive and accept slot values wider than 32 bits. When switching addressing
modes, clear the stored selector with `""` in the same update that sets the new
one. (`2.0.4`)

```json
{"slot":"","token_label":"hsm-token"}
```

### Managed-key API representation

`GET sys/managed-keys/:type/:name` returns usage names rather than integers:
`encrypt`, `decrypt`, `sign`, `verify`, `wrap`, `unwrap`, `generate_random`, and
`mac`. Update clients that decode numeric usage IDs. (`2.0-changelog`)

Transit CSR-signing and certificate-chain-setting endpoints accept Enterprise
managed keys, not only locally stored Transit keys. (`2.0.4`)

## KMIP

KMIP APIs manage multiple client-verification CAs and import external CAs.
Enterprise also exposes an experimental endpoint for executing KMIP requests.
(`2.0-changelog`)

## MSSQL external key management

The MSSQL EKM provider lets administrators choose which Transit key versions
wrap and unwrap SQL Server data-encryption keys, which helps restore encrypted
backups. (`1.21`)

## FIPS, TLS, and Common Criteria

FIPS builds use a FIPS 140-3 cryptographic module and compliant algorithms. The
Go TLS stack supports X25519MLKEM768 hybrid post-quantum key agreement.
(`1.19-changelog`)

Enterprise `common_criteria_mode` restricts listener TLS cipher suites. For
PKI, it validates the full chain, can enable validation-time checks, treats
`NotBefore` as zero, enforces minimum key usages for extended-key-usage sets,
and rejects uploaded certificates without a chain of trust.
(`2.0-changelog`)
