# Security, Networking, and Interop

Compatibility guidance is attributed to `10.0-guides`; new APIs are attributed
to `10.0`.

## Cryptography Compatibility

- Composite ML-DSA moved to draft-08.
- The ML-DSA and SLH-DSA `SecretKey` members were renamed to `PrivateKey`.
- `CoseSigner.Key` and key parameters on `X509Certificate` and `PublicKey` may be
  null; handle absence explicitly.
- Unix requires OpenSSL 1.1.1 or later.
- OpenSSL cryptographic primitives are unsupported on macOS.
- `X500DistinguishedName` validation is stricter.
- The OpenSSL override variable is `DOTNET_OPENSSL_VERSION_OVERRIDE`.

## Algorithm-Specific Certificate Lookup and PFX Export

`X509Certificate2Collection.FindByThumbprint` accepts `HashAlgorithmName`. Prefer
it to the SHA-1-oriented `Find(FindByThumbprint, ...)`, particularly to avoid
ambiguity between same-length hashes. `X509Certificate.ExportPkcs12` accepts a
`Pkcs12ExportPbeParameters` preset or custom `PbeParameters`, allowing an explicit
choice between broadly compatible 3DES/SHA-1 and modern AES-256/SHA-256 output.

```csharp
var matches = certificates.FindByThumbprint(HashAlgorithmName.SHA256, thumbprint);
byte[] pfx = certificate.ExportPkcs12(
    Pkcs12ExportPbeParameters.Pbes2Aes256Sha256, password);
```

## Post-Quantum Cryptography APIs

`MLKem`, `MLDsa`, and `SlhDsa` use static key generation and import methods rather
than deriving from `AsymmetricAlgorithm`. Check each type's `IsSupported` property:
availability requires OpenSSL 3.5 or later, or Windows CNG with PQC support.
`MLDsa` and `SlhDsa` remain experimental under SYSLIB5006, and some `MLKem`
methods are experimental.

```csharp
if (MLKem.IsSupported)
{
    using var key = MLKem.GenerateKey(MLKemAlgorithm.MLKem768);
}
```

## AES KeyWrap with Padding

`Aes` implements RFC 5649 AES-KWP through methods such as
`DecryptKeyWrapPadded`. When writing into a caller-provided destination, the
method returns the unwrapped key length.

```csharp
using Aes aes = Aes.Create();
aes.SetKey(keyEncryptionKey);
int length = aes.DecryptKeyWrapPadded(wrappedKey, destination);
```

## macOS Client TLS 1.3

On macOS, `SslStream` and `HttpClient` clients can opt into TLS 1.3 through
Network.framework by using the `System.Net.Security.UseNetworkFramework`
AppContext switch or `DOTNET_SYSTEM_NET_SECURITY_USENETWORKFRAMEWORK=1`. The opt-in
is client-only, can remove TLS 1.0/1.1 availability, and can change buffering,
cancellation, zero-byte-read, and IDN behavior.

```csharp
AppContext.SetSwitch("System.Net.Security.UseNetworkFramework", true);
```

## Networking Defaults and Validation

- Trimmed publications disable HTTP/3 by default.
- Browser HTTP clients stream responses by default.
- `Uri` no longer imposes its former length limits.
- `MailAddress` rejects addresses containing consecutive dots.

## Native-Library and COM Interop

- Single-file apps no longer probe the executable directory for native libraries.
- `DllImportSearchPath.AssemblyDirectory` searches only the assembly directory.
- Casting an `IDispatchEx` COM object to `IReflect` fails.

Package native libraries where the loader searches for them and avoid assuming
that the app executable and managed assembly have the same directory.
