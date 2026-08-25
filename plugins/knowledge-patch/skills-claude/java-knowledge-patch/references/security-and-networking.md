# Security, Cryptography, and Networking

Use this reference for native-access policy, unsafe memory access, standard
cryptographic APIs, trust-store migrations, provider changes, and HTTP/3.

## Native and unsafe memory access

JDK 24 warns when code uses JNI or restricted Foreign Function and Memory
operations without explicitly enabling native access (24). Update
native-library deployment flags and module scopes before the planned
deny-by-default policy makes the same access fail.

The first run-time use of terminally deprecated `sun.misc.Unsafe`
memory-access methods emits a warning in JDK 24 (24). Use that warning to find
dependencies that need supported memory-access replacements or upgrades.

Grant the smallest required native-access scope. Do not suppress warnings
without identifying the calling module and its migration path.

## Standard cryptographic APIs

### Key derivation

The standard Key Derivation Function API is previewed in JDK 24 (24) and
becomes permanent in JDK 25 (25-migration). Preview callers require
`--enable-preview` at compile and run time and must be recompiled per release;
final callers no longer need that flag solely for KDF.

### Post-quantum algorithms

JDK 24 implements ML-KEM, the Module-Lattice-Based Key Encapsulation Mechanism
(24).

JDK 24 also implements ML-DSA, the Module-Lattice-Based Digital Signature
Algorithm (24).

Validate protocol interoperability, key formats, provider selection, and
algorithm policy when introducing either algorithm.

### PEM encodings

The JDK 25 PEM API encodes and decodes keys, certificates, and revocation
lists (25). It is preview in JDK 25 and evolves to a second preview in JDK 26
(26-migration), so update and recompile callers for the destination release.

## Trust-store changes

The default trust store removes these roots in JDK 25 (25-migration):

- Baltimore CyberTrust root
- two Camerfirma root certificates

JDK 26 removes four AffirmTrust roots and the Sun Microsystems JCE
code-signing root (26-migration).

Inventory real certificate chains and code-signing dependencies. A root being
present in an older JDK does not establish that it remains available in a
newer default trust store. Add an explicit private trust configuration only
after validating ownership, policy, and the intended chain.

## Provider and algorithm requirements

SunPKCS11 removes its PBE-related `SecretKeyFactory` implementations in JDK 25
(25-migration). Audit code that assumes those algorithms are supplied by that
provider.

JDK 26 security requirements drop older DESede and PKCS1Padding requirements
and add PBES2 requirements (26-migration). These are availability requirements,
not a promise that every historical provider algorithm remains. Verify the
providers in the deployed runtime and test the exact transformations used by
the application.

## JNDI hardening

JNDI remote code downloading is permanently disabled (24-migration), and the
`java.naming.rmi.security.manager` compatibility property is removed. Design
naming lookups around local classes and explicitly trusted data rather than
trying to recover remote class loading.

## HTTP/3

The standard HTTP Client can use HTTP/3 in JDK 26 (26-migration). HTTP/3 uses
QUIC over UDP, so a successful HTTP/2 deployment does not prove that the new
transport path works.

Test all of the following in a production-like environment:

- outbound and inbound UDP network policy
- proxies and firewalls
- connection fallback paths
- certificate validation and hostname handling
- tracing, metrics, logging, and packet-level observability

Verify both the HTTP/3 success path and graceful fallback when QUIC is blocked
or degraded.

## Security migration checklist

1. Locate JNI, restricted Foreign Function and Memory, and `Unsafe` callers.
2. Narrow native-access grants to the modules that require them.
3. Match preview flags to the KDF or PEM API status in the selected JDK.
4. Test ML-KEM and ML-DSA interoperability before enabling them in protocols.
5. Validate deployed certificate chains against the destination trust store.
6. Test required algorithms against the actual provider set.
7. Remove JNDI remote-code-loading assumptions.
8. Exercise HTTP/3 through the real UDP, proxy, firewall, and observability
   path.
