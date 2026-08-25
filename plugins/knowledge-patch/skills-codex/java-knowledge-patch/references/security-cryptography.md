# Security and Cryptography

Use this reference for native-access enforcement, reflective mutation,
Security Manager migration, post-quantum algorithms, PEM handling, trust-store
changes, and provider capability audits.

## Security Manager removal path

The Security Manager is permanently disabled in 24. Attempting to enable it is
an error. Its APIs remain only as migration aids before eventual removal; do
not design new authorization or sandbox behavior around them.

The 25-migration deprecates legacy permission classes associated with the
disabled Security Manager for removal. Migrate both startup configuration and
code that constructs or inspects the legacy permission model.

## Native access and internal memory APIs

JDK 24 warns when JNI or restricted Foreign Function and Memory operations are
used without explicitly enabled native access. Inventory native-library load
paths and grant access deliberately before the planned deny-by-default policy
makes an unaddressed warning an operational failure.

The first runtime use of terminally deprecated `sun.misc.Unsafe`
memory-access methods emits a warning in 24. Use the first warning to identify
the direct dependency or framework that needs migration; suppressing the
signal does not remove reliance on the terminally deprecated methods.

## Final-field mutation

Deep reflection that mutates a `final` field warns in 26-migration.
`--enable-final-field-mutation` grants the capability to selected modules or
scopes. `--illegal-final-field-mutation` controls behavior when mutation
occurs without that grant.

Use the narrowest grant during migration. Move frameworks toward supported
construction or serialization mechanisms instead of treating a broad grant
as permanent configuration.

## Key derivation and post-quantum algorithms

The standard Key Derivation Function API is preview in 24, requiring
`--enable-preview` at compilation and runtime and recompilation for each JDK
release. It becomes permanent in 25-migration.

JDK 24 implements both of these quantum-resistant algorithms:

- ML-KEM, the Module-Lattice-Based Key Encapsulation Mechanism.
- ML-DSA, the Module-Lattice-Based Digital Signature Algorithm.

Validate provider selection, key formats, protocol integration, and
interoperability in the actual deployment rather than treating platform
availability as automatic application adoption.

## PEM encodings

The 25 batch adds an API for encoding and decoding keys, certificates, and
revocation lists in PEM form. PEM encodings remain preview in 25-migration and
reach a second preview in 26-migration, so code written for the earlier form
must be updated and recompiled for the next preview revision.

## Trust-store removals

The 25-migration removes the Baltimore CyberTrust root and two Camerfirma root
certificates from the default trust store. Audit real server and client chains,
including private services whose chain may depend on a formerly bundled root.

The 26-migration removes four AffirmTrust roots and the Sun Microsystems JCE
code-signing root. Re-run certificate-chain and signed-provider validation on
the target runtime; a chain that worked with an older default store may now
need a different chain or an explicitly managed trust anchor.

## Provider and algorithm requirements

SunPKCS11 removes its PBE-related `SecretKeyFactory` implementations in
25-migration. Applications must audit provider-qualified requests and any
assumption that those PBE algorithms are supplied by SunPKCS11.

In 26-migration, platform security requirements drop older DESede and
PKCS1Padding requirements and add PBES2 requirements. This changes what the
platform promises, not necessarily every provider's implementation at once.
Verify provider capabilities directly rather than inferring availability from
older requirements.

## Security upgrade checklist

1. Remove Security Manager enablement and inventory legacy permission-class
   dependencies.
2. Exercise every JNI and restricted Foreign Function and Memory call path;
   make native-access grants explicit and narrow.
3. Attribute `sun.misc.Unsafe` warnings to the dependency that issues the
   terminally deprecated memory operation.
4. Locate frameworks that mutate final fields and grant only the modules or
   scopes needed during migration.
5. Compile preview cryptography against the exact deployment JDK and
   recompile on every preview revision.
6. Validate PEM interoperability and cryptographic provider selection.
7. Test complete production certificate chains against the target default or
   managed trust store.
8. Probe required PBE, PBES2, DESede, and PKCS1Padding algorithms on the
   selected provider instead of relying on historical platform requirements.
