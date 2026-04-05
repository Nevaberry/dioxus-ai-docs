# Post-Quantum Cryptography (AlmaLinux 10+)

AlmaLinux 10 enables post-quantum cryptography by default through system-wide crypto policies. No manual configuration is required.

## Enabled Algorithms

| Algorithm | Standard | Purpose |
|-----------|----------|---------|
| ML-KEM (Kyber) | FIPS 203 | Key encapsulation (key exchange) |
| ML-DSA (Dilithium) | FIPS 204 | Digital signatures |
| SLH-DSA (SPHINCS+) | FIPS 205 | Stateless hash-based signatures |

## Implementation Details

### OpenSSL 3.5

OpenSSL 3.5 in AlmaLinux 10 includes native PQC support:

- ML-KEM, ML-DSA, and SLH-DSA providers built in
- Hybrid ML-KEM is included in the default TLS group list
- TLS connections automatically negotiate PQC key exchange when both sides support it

### RPM Signatures

RPMv6 introduces PQC signature support using Sequoia PGP tools, enabling quantum-resistant package verification.

### System-Wide Crypto Policies

PQC algorithms are enabled across all crypto policy levels (DEFAULT, FUTURE, FIPS, etc.). The policy framework ensures consistent PQC support across all system components:

```bash
# View current crypto policy
update-crypto-policies --show

# PQC is enabled in all policies by default — no changes needed
```
