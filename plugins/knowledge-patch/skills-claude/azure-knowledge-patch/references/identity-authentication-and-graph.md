# Identity, authentication, and Microsoft Graph

## Mandatory MFA and Microsoft Graph migration

### Azure AD Graph retirement (`entra-authentication-and-graph`)

Azure AD Graph fully retired August 31, 2025. The extended-access opt-in for
new and existing applications ended with retirement; migrate all remaining
callers to Microsoft Graph.

Since January 7, 2025, the Entra admin center app-registration manifest page
accepts the Microsoft Graph shape, except for personal-Microsoft-account apps.
Key manifest conversions are:

| Azure AD Graph | Microsoft Graph |
| --- | --- |
| `accessTokenAcceptedVersion` | `api.requestedAccessTokenVersion` |
| `oauth2Permissions` | `api.oauth2PermissionScopes` |
| `acceptMappedClaims` | `api.acceptMappedClaims` |
| `knownClientApplications` | `api.knownClientApplications` |
| `preAuthorizedApplications` | `api.preAuthorizedApplications` |
| ID-token implicit flag | `web.implicitGrantSettings.enableIdTokenIssuance` |
| access-token implicit flag | `web.implicitGrantSettings.enableAccessTokenIssuance` |
| `replyUrlsWithType` | platform `redirectUris` under `web`, `spa`, or `publicClient` |

Also rename `allowPublicClient` to `isFallbackPublicClient`,
`informationalUrls` to `info`, and `name` to `displayName`; move `logoUrl` into
`info`, `logoutUrl` into `web`, and `signInUrl` to `web.homePageUrl`. Remove
`errorUrl`. `replyUrlsWithType` signals the old shape;
`implicitGrantSettings` signals the Graph shape.

### ARM mandatory MFA

Phase 1 covered Azure, Entra, and Intune portal CRUD from October 2024, with
Microsoft 365 admin center from February 2025. Phase 2 began October 1, 2025
for create/update/delete through Azure CLI, Azure PowerShell, mobile, IaC,
SDKs, and control-plane REST. Read operations do not require MFA.

Enforcement is server-side at `https://management.azure.com` and generally not
Microsoft Graph. It currently applies to public Azure, not sovereign clouds.
Use Azure CLI 2.76+ or Azure PowerShell 14.3+ for better claims handling.

Every user identity is covered: emergency accounts, guests, test tenants,
eligible users, and Conditional Access-excluded users. Managed identities and
service principals are outside both phases. Move user-service-account
automation to a workload identity and equip emergency users with passkey or
certificate MFA.

External MFA works only when its federation supplies an MFA assertion such as
`multipleauthn`; legacy Conditional Access custom controls do not satisfy this.

### ROPC cannot satisfy MFA

Username/password authentication cannot complete a claims challenge. Public-
client username/password APIs are deprecated in MSAL .NET 4.74.0, Go 1.6.0,
Java 1.24.0, Python 1.35.0, and Node.js 3.2.3. Remaining confidential-client
variants still cannot satisfy MFA.

## Azure Identity SDKs (`identity-sdk-authentication`)

### Constrain `DefaultAzureCredential`

Current .NET, Go, Java, JavaScript, and Python SDKs read
`AZURE_TOKEN_CREDENTIALS`: `dev` selects developer-tool credentials, `prod`
selects deployed-service credentials, and a credential class name selects only
that credential.

```bash
AZURE_TOKEN_CREDENTIALS=WorkloadIdentityCredential
```

Go `RequireAzureTokenCredentials` and Python `require_envvar` can require the
variable. Java `requireEnvVars` and JavaScript `requiredEnvVars` can fail when
selected variables are empty. .NET can use a custom selection-variable name.

### Brokered development credentials

.NET, Java, JavaScript, and Python restore `VisualStudioCodeCredential` through
broker packages and can append the signed-in Windows account. JavaScript also
requires `useIdentityPlugin`. .NET always includes a BrokerCredential position
and throws if reached without `Azure.Identity.Broker`. .NET/Java remove
`SharedTokenCacheCredential` from the default chain and deprecate its APIs.

### Password-credential deprecation

All five SDKs deprecate `UsernamePasswordCredential`. .NET marks
`AZURE_USERNAME`/`AZURE_PASSWORD` obsolete; Java/JavaScript warn when
EnvironmentCredential is configured with username/password.

### Claims-challenge differences

Java and Python `AzureDeveloperCliCredential` forward claims to `azd`; Java
needs Azure Developer CLI 1.18.1+. .NET, JavaScript, and Go reject claims for
that credential. Documented Azure CLI and Azure PowerShell credentials also
return authentication/availability errors rather than acquiring a challenged
token. A JavaScript beta retains the MSAL error in
`AuthenticationRequiredError.cause`, including `claims`.

### Preview AKS workload-identity proxy

Preview WorkloadIdentityCredential can redirect through an AKS proxy, avoiding
the per-application federated-credential limit. Current switches are .NET
`IsAzureProxyEnabled`, Java `enableAzureProxy()`, JavaScript
`enableAzureProxy`, and Python `enable_azure_proxy`. Earlier beta names changed.
.NET/JavaScript require direct `WorkloadIdentityCredential`, not DAC or MIC.
Go 1.14 removed beta `EnableAzureProxy` from stable and plans a later beta.

### Managed-identity probing and retries

When DAC is constrained to `ManagedIdentityCredential`, all languages skip the
IMDS availability probe and use standalone retry behavior. .NET, JavaScript,
and Python retry HTTP 410 for at least 70 seconds; Go's default IMDS retry is
about 70 seconds. Size startup timeouts accordingly.

JavaScript/Python reject user-assigned identity in Service Fabric rather than
ignoring it. .NET deprecates ambiguous constructors in favor of overloads
taking `ManagedIdentityId` or options.

### CLI subscription and SDK-specific changes

.NET, Java, JavaScript, and Python AzureCliCredential options select a CLI
subscription by ID/name. Go 1.13 adds AzurePowerShellCredential.

All .NET Azure.Identity types moved to Azure.Core with type forwarding. New
experimental configuration/DI and appsettings schema exist, but
`AddAzureClient`, `AddKeyedAzureClient`, and `WithAzureCredential` return
`IClientBuilder`, not `IHostApplicationBuilder`.

.NET ClientCertificateCredential can load Windows certificate-store or macOS
Keychain certs with `cert:/StoreLocation/StoreName/Thumbprint`.

Python 1.26 beta accepts transport policy overrides, per-call/per-retry
policies, and adds RequestIdPolicy with unique `x-ms-client-request-id`.

### Runtime floors

Go identity 1.14 requires Go 1.25. Python identity 1.22 requires Python 3.9+.
JavaScript identity 4.7 emits CommonJS and ESM, 4.9 adds `workerd` exports, and
4.13.1 upgrades MSAL Node/Browser to 5.x.

## Azure CLI authentication

### Managed identity migration

- `2.68.0` removes old managed-identity account state from CLI 2.0.50 or
  earlier; run `az login --identity` again.
- `2.69.0` deprecates a managed-identity ID passed to `az login --username`;
  use `--client-id`, `--object-id`, or `--resource-id`.
- `2.73.0` enforces that migration and rejects user-assigned identity IDs in
  `--username`.
- `2.83.0` managed-identity login stops retrieving the machine FQDN, avoiding
  hangs caused by network misconfiguration.

### Claims, tenant, subscription, and SSH

- `2.76.0` adds interactive `az login --claims-challenge`.
- `2.77.0` allows `az account get-access-token --tenant` to use the current
  tenant for Cloud Shell/managed identity, and claims-challenge login works in
  device-code flow.
- `2.86.0` login adds `--subscription` and `--skip-subscription-discovery` to
  filter or avoid subscription discovery.
- `2.88.0` `az ssh` again fails explicitly for unsupported managed-identity and
  Cloud Shell certificate flows; handle the errors.

### Entra applications and service principals

- `2.68.0` `az ad app create/update --requested-access-token-version` sets the
  desired access-token version.
- `2.72.0` `az ad sp create-for-rbac` adds
  `--service-management-reference` and `--create-password`; pass false to avoid
  a password credential.

### Federated and managed identities

- `2.74.0` identity federated-credential create/update supports claims-matching
  expressions; Monitor action groups add incident receivers plus system/user
  assigned identities.
- `2.82.0` identity create adds `--isolation-scope`.
- `2.88.0` identity create adds `--resource-restriction` for assignment
  restrictions.

## Azure PowerShell (`powershell-authentication`)

### Tokens and challenged sign-in

Az.Accounts 5.0 changes `Get-AzAccessToken` output token from plaintext to
`SecureString`; 5.0.1 makes `-AsSecureString` always return SecureString.
Az.Accounts 5.2 adds `Connect-AzAccount -ClaimsChallenge`.

### REST operations

Az.Accounts 5.3 adds server-side pagination to `Invoke-AzRestMethod` with
`-Paginate`; the 4.0 line added long-running-operation handling.

### Cloud endpoints and SSH certificate scope

`Add-AzEnvironment`/`Set-AzEnvironment` accept
`AzureAppConfigurationEndpointSuffix` and
`AzureAppConfigurationEndpointResourceId`. Mooncake/USGov received those
endpoints in 4.1.

Az.Accounts 5.1 adds `Set-AzEnvironment -SshAuthScope`. From 5.3.4 SSH
certificate auth works across all Azure clouds without that setting; 5.5 adds
service-principal support in `SshCredentialFactory`.

Az.Accounts 4.0 removes the `Resolve-Error` alias; call `Resolve-AzError`.

## Cloud and Graph endpoint behavior

`2.75.0` cloud register/update adds Microsoft Graph resource-ID endpoint and
`--skip-endpoint-discovery`. `2.73.0` resource-manager endpoint discovery
automatically finds data-plane endpoints and omits the old `gallery` endpoint.
`2.76.0` the US Government profile uses
`https://graph.microsoftazure.us/` as its Azure AD Graph resource ID.

Treat endpoint discovery and the legacy Azure AD Graph audience as separate
from migration of application calls to Microsoft Graph.
