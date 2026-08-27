# Security, Cryptography, and Networking

Compatibility notes are attributed to `10.0-guides`, APIs to `10.0`, and the
servicing release to `10.0.11`.

## Security Servicing

.NET 10.0.11 addresses the following vulnerabilities:

- Remote code execution: CVE-2026-70354 and CVE-2026-62897.
- Elevation of privilege: CVE-2026-62886, CVE-2026-62871, and CVE-2026-62909.
- Information disclosure: CVE-2026-62898, CVE-2026-62900, and CVE-2026-62902.
- Security feature bypass: CVE-2026-62899.
- Denial of service: CVE-2026-62901.

Update deployed runtimes and refresh .NET 10 container images. Merely installing an
SDK on a build machine does not update already-published framework-dependent hosts or
existing runtime/container deployments.

Runtime 10.0.11 is included in SDK 10.0.400, 10.0.303, and 10.0.111; those SDKs also
install matching updated .NET and ASP.NET Core runtimes, so separate runtime packages
are unnecessary on that machine.

## Cryptography Compatibility

Composite ML-DSA moved to draft-08. Confirm external peers and stored key/signature
formats use the same draft.

The ML-DSA and SLH-DSA `SecretKey` members were renamed to `PrivateKey`. Update source
and reflection-based member lookup.

`CoseSigner.Key` and key parameters on `X509Certificate` and `PublicKey` can be null.
Update nullable handling instead of assuming a key is always present.

On Unix, .NET requires OpenSSL 1.1.1 or later. OpenSSL cryptographic primitives are
not supported on macOS. Validate support with the API/platform path actually used.

`X500DistinguishedName` validation is stricter. Reject or normalize invalid names
rather than relying on earlier permissive parsing.

The OpenSSL override environment variable is
`DOTNET_OPENSSL_VERSION_OVERRIDE`. Replace older override names in launch and
deployment configuration.

## Algorithm-Specific Certificate Lookup and PFX Export

In `10.0`, `X509Certificate2Collection.FindByThumbprint` accepts a
`HashAlgorithmName`. Prefer it to `Find(FindByThumbprint, ...)`, whose SHA-1-only
behavior can confuse same-length hash values.

`X509Certificate.ExportPkcs12` accepts either a `Pkcs12ExportPbeParameters` preset or
custom `PbeParameters`. Choose deliberately between broadly compatible 3DES/SHA-1 and
modern AES-256/SHA-256 output according to the recipient's capabilities.

```csharp
var matches = certificates.FindByThumbprint(HashAlgorithmName.SHA256, thumbprint);
byte[] pfx = certificate.ExportPkcs12(
    Pkcs12ExportPbeParameters.Pbes2Aes256Sha256, password);
```

## Post-Quantum Cryptography APIs

The `10.0` types `MLKem`, `MLDsa`, and `SlhDsa` expose static key generation/import
methods rather than deriving from `AsymmetricAlgorithm`. Check each type's
`IsSupported` property: availability requires OpenSSL 3.5+ or Windows CNG with PQC
support.

`MLDsa` and `SlhDsa` remain experimental under `SYSLIB5006`; some `MLKem` methods are
also experimental. Keep warnings and support checks visible in application policy.

```csharp
if (MLKem.IsSupported)
{
    using var key = MLKem.GenerateKey(MLKemAlgorithm.MLKem768);
}
```

## AES KeyWrap with Padding

In `10.0`, `Aes` implements RFC 5649 AES-KWP with APIs such as
`DecryptKeyWrapPadded`. When writing into caller-provided storage, the method returns
the unwrapped key length; use only that portion of the destination.

```csharp
using Aes aes = Aes.Create();
aes.SetKey(keyEncryptionKey);
int length = aes.DecryptKeyWrapPadded(wrappedKey, destination);
```

## Networking Defaults and Validation

Trimmed publications disable HTTP/3 by default. If HTTP/3 is required, configure it
explicitly and verify the trimmed output rather than only an untrimmed development
build.

Browser HTTP clients stream responses by default. Do not assume the full response is
buffered before consumer code begins reading it.

`Uri` no longer applies its former length limits. Apply application-specific limits
where resource usage or protocol constraints require them.

`MailAddress` rejects addresses containing consecutive dots. Treat newly rejected
input as invalid rather than preprocessing it into acceptance without policy review.

## Opt-In macOS Client TLS 1.3

In `10.0`, macOS clients can use TLS 1.3 with `SslStream` and `HttpClient` by opting
into Network.framework:

```csharp
AppContext.SetSwitch("System.Net.Security.UseNetworkFramework", true);
```

The equivalent environment variable is
`DOTNET_SYSTEM_NET_SECURITY_USENETWORKFRAMEWORK=1`.

This path is client-only. It can remove TLS 1.0/1.1 availability and change
buffering, cancellation, zero-byte-read, and internationalized-domain-name behavior.
Exercise those behaviors before enabling it broadly.
