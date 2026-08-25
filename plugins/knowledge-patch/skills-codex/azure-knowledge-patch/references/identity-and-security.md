# Identity and security

Use this reference for current compatibility details and exact command or schema changes.

## Authorization and RBAC

### Management-group role-assignment inheritance (2.71.0)

`az role assignment list` now includes assignments inherited from management
groups, so consumers may see additional results. The command also announces
an upcoming breaking change for `--include-classic-administrators`.

### Role-assignment deletion is no longer implicitly global (2.68.0)

In a breaking safety change, `az role assignment delete` no longer deletes
all role assignments by default. Scripts that intended bulk deletion must
not rely on invoking the command without explicit selection criteria.

### Role-assignment operations without expansion queries (2.72.0)

`az role assignment list --fill-principal-name false` omits `principalName`
and bypasses Microsoft Graph, while `--fill-role-definition-name false` omits
`roleDefinitionName` and bypasses the role-definition query. List and delete
also accept `--assignee-object-id` instead of `--assignee` to avoid a
Microsoft Graph lookup.

## Azure Identity SDK authentication

### .NET certificates from platform stores (identity-sdk-authentication)

`ClientCertificateCredential` can load a certificate from the Windows
certificate store or macOS Keychain by using a
`cert:/StoreLocation/StoreName/Thumbprint` path instead of a certificate
file.

```text
cert:/CurrentUser/My/E661583E8FABEF4C0BEF694CBC41C28FB81CD870
```

### .NET identity assembly and client composition (identity-sdk-authentication)

All .NET `Azure.Identity` types moved to `Azure.Core` with type forwarding,
so existing references continue to work. The package also adds experimental
configuration and dependency-injection integration plus an `appsettings.json`
schema, but `AddAzureClient`, `AddKeyedAzureClient`, and
`WithAzureCredential` now return `IClientBuilder` rather than
`IHostApplicationBuilder`.

### Brokered development authentication replaces legacy caches (identity-sdk-authentication)

.NET, Java, JavaScript, and Python restored `VisualStudioCodeCredential`
through their broker packages and can add the signed-in Windows account at
the end of `DefaultAzureCredential`; JavaScript also requires
`useIdentityPlugin`. .NET now always represents `BrokerCredential` in the
chain and throws if it is reached without `Azure.Identity.Broker`, while .NET
and Java removed `SharedTokenCacheCredential` from the default chain and
deprecated its public APIs.

### Claims challenges differ among tool-backed credentials (identity-sdk-authentication)

Java and Python `AzureDeveloperCliCredential` can forward claims to `azd`;
Java requires Azure Developer CLI 1.18.1 or newer. The .NET, JavaScript, and
Go implementations instead reject claims for that credential, and the
documented `AzureCliCredential` and `AzurePowerShellCredential`
implementations also return an authentication or availability error rather
than acquiring a claims-challenge token. The latest JavaScript beta preserves
the underlying MSAL error as `AuthenticationRequiredError.cause`, exposing
its `claims` value to callers.

### Constraining `DefaultAzureCredential` by environment (identity-sdk-authentication)

The .NET, Go, Java, JavaScript, and Python identity SDKs now recognize
`AZURE_TOKEN_CREDENTIALS`: `dev` limits the chain to developer-tool
credentials, `prod` limits it to deployed-service credentials, and a
credential class name selects only that credential.

```bash
AZURE_TOKEN_CREDENTIALS=WorkloadIdentityCredential
```

Go's `RequireAzureTokenCredentials` and Python's `require_envvar` can require
this variable, while Java's `requireEnvVars` and JavaScript's
`requiredEnvVars` can fail construction when selected environment variables
are empty. .NET can instead construct `DefaultAzureCredential` with a custom
environment-variable name that uses the same selection rules.

### Identity SDK runtime and module requirements (identity-sdk-authentication)

Go identity 1.14 requires Go 1.25, and Python identity 1.22 drops Python 3.8
in favor of Python 3.9 or newer. JavaScript identity 4.7 emits both CommonJS
and native ESM, 4.9 adds `workerd` exports for Cloudflare, and 4.13.1 upgrades
its MSAL Node and Browser dependencies to the 5.x line.

### Managed-identity probing, retries, and validation (identity-sdk-authentication)

When `AZURE_TOKEN_CREDENTIALS=ManagedIdentityCredential`, all five
`DefaultAzureCredential` implementations skip the IMDS availability probe
and use standalone managed-identity retry behavior. .NET, JavaScript, and
Python retry IMDS HTTP 410 responses for at least 70 seconds, while Go's
default IMDS retry window is approximately 70 seconds; startup timeouts must
allow for that delay.

JavaScript and Python now reject user-assigned identity configuration in
Service Fabric instead of silently ignoring it. .NET also deprecates its
ambiguous legacy managed-identity constructors in favor of overloads taking
`ManagedIdentityId` or `ManagedIdentityCredentialOptions`.

### Password credentials are deprecated for MFA (identity-sdk-authentication)

`UsernamePasswordCredential` is deprecated across all five SDKs because the
ROPC flow cannot satisfy multifactor authentication. .NET also marks
`AZURE_USERNAME` and `AZURE_PASSWORD` obsolete, and Java and JavaScript warn
when username/password configuration is used through `EnvironmentCredential`.

### Preview AKS workload-identity token proxy (identity-sdk-authentication)

Preview `WorkloadIdentityCredential` APIs can redirect token acquisition
through an AKS proxy, avoiding the per-application federated-credential limit.
The current beta switches are .NET `IsAzureProxyEnabled`, Java
`enableAzureProxy()`, JavaScript `enableAzureProxy`, and Python
`enable_azure_proxy`; earlier beta names were renamed. The .NET and
JavaScript previews require using `WorkloadIdentityCredential` directly,
not `DefaultAzureCredential` or `ManagedIdentityCredential`. Go 1.14 removed
its beta `EnableAzureProxy` option from the stable release and announces its
return in a later beta.

### Python credential pipeline customization (identity-sdk-authentication)

Python 1.26 beta credentials accept overrides for headers, logging, proxy,
user-agent, hook, and retry policies, plus `per_call_policies` and
`per_retry_policies`. The same beta adds `RequestIdPolicy` by default so each
request carries a unique `x-ms-client-request-id`.

### Subscription-aware CLI credentials (identity-sdk-authentication)

.NET, Java, JavaScript, and Python `AzureCliCredential` options can select the
Azure CLI subscription by ID or name instead of always using its ambient
selection. Go 1.13 also adds `AzurePowerShellCredential` for the identity
currently signed in to Azure PowerShell.

## Azure PowerShell authentication

### `Resolve-Error` alias removed (powershell-authentication)

Az.Accounts 4.0 removed the `Resolve-Error` alias; scripts must invoke
`Resolve-AzError` directly.

### Access tokens are secure strings by default (powershell-authentication)

Az.Accounts 5.0 changed the access token in `Get-AzAccessToken` output from
plain text to a `SecureString` by default. From 5.0.1,
`-AsSecureString` also always produces a `SecureString`.

```powershell
Get-AzAccessToken
Get-AzAccessToken -AsSecureString
```

### Azure App Configuration endpoints in cloud environments (powershell-authentication)

`Add-AzEnvironment` and `Set-AzEnvironment` accept
`AzureAppConfigurationEndpointSuffix` and
`AzureAppConfigurationEndpointResourceId`, allowing custom environments to
define their Azure App Configuration endpoints. Mooncake and USGov
environments also received their App Configuration resource-ID and suffix
endpoints in Az.Accounts 4.1.

### Claims-challenge sign-in (powershell-authentication)

Az.Accounts 5.2 added `Connect-AzAccount -ClaimsChallenge` so sign-in can
satisfy an MFA claims challenge.

```powershell
Connect-AzAccount -ClaimsChallenge $claimsChallenge
```

### REST pagination and long-running operations (powershell-authentication)

Az.Accounts 5.3 added server-side pagination to `Invoke-AzRestMethod` through
its `-Paginate` parameter. The 4.0 line also added long-running-operation
support for REST invocation.

### SSH certificate authentication across clouds and identities (powershell-authentication)

Az.Accounts 5.1 introduced `Set-AzEnvironment -SshAuthScope <String>` for
selecting the authentication scope used by Az SSH cmdlets. From 5.3.4, SSH
certificate authentication works across all Azure clouds without configuring
that setting, and 5.5 adds service-principal support to SSH certificate
generation in `SshCredentialFactory`.

## CLI authentication

### Authentication flow changes (2.77.0)

`az account get-access-token --tenant` now accepts the account's current
tenant for Cloud Shell and managed-identity accounts. The existing `az login
--claims-challenge` option can also be used in the device-code flow.

### Claims-challenge login (2.76.0)

`az login --claims-challenge` supports interactive authentication that must
satisfy a supplied claims challenge.

### Explicit SSH failures (2.88.0)

`az ssh` once again fails explicitly for unsupported managed-identity and
Cloud Shell SSH-certificate flows; automation must handle these as errors.

### Subscription-filtered login (2.86.0)

`az login` accepts `--subscription` and `--skip-subscription-discovery` to
filter subscription handling during login, including avoiding subscription
discovery when it is not needed.

## Identity and security operations

### Azure US Government Graph endpoint (2.76.0)

The `AZURE_US_GOV_CLOUD` profile now sets `active_directory_graph_resource_id`
to `https://graph.microsoftazure.us/`.

### Base64 key-operation digests (2.68.0)

`az keyvault key sign` and `az keyvault key verify` now accept a base64-encoded
string in `--digest`, so callers no longer need a different representation
for that input.

### Classic-administrator option removed (2.73.0)

`az role assignment list` no longer accepts
`--include-classic-administrators`.

### Entra application access-token version (2.68.0)

`az ad app create` and `az ad app update` accept
`--requested-access-token-version`, allowing the requested token version to
be set through Azure CLI.

### Service-principal creation without a password (2.72.0)

`az ad sp create-for-rbac` accepts `--service-management-reference` and
`--create-password`; pass `--create-password false` to avoid creating a
password credential.

## Key Vault and managed HSM

### Cloud HSM private-endpoint connections (2.89.0)

Private-endpoint connection operations now recognize the
`Microsoft.HardwareSecurityModules/cloudHsmClusters` provider.

### Default SKR policy for Key Vault keys (2.82.0)

`az keyvault key create` and `import` accept `--default-data-disk-policy` to
configure the default SKR policy for data disks.

### Key Vault AES output (2.88.0)

`az keyvault key show` and `list` now include the AES key size in their
output, so fixed-schema consumers must tolerate the additional value.

### Key Vault network-rule updates (2.69.0)

When `--default-action Deny` is supplied to `az keyvault update` or
`az keyvault update-hsm`, the command no longer overwrites an explicitly
selected `--bypass` value with its default.

### Managed HSM C SKU family (2.71.0)

`az keyvault create` supports the C SKU family when creating a Managed HSM.

### Managed HSM external keys (2.88.0)

The preview `az keyvault ekm-connection` group manages External Key Manager
connections. `az keyvault key create --external-key-id` creates an
EKM-backed external key on Managed HSM.

### Managed HSM IP network rules (2.78.0)

`az keyvault create --network-acls-ips` can set Managed HSM IP rules at
creation, and `network-rule add/remove/list/wait` now supports Managed HSM.

## Key Vault API and access control

### Control-plane API lifecycle (key-vault-api-and-access-control)

Stable API `2026-02-01` and preview API `2026-03-01-preview` are available in
public Azure, Azure operated by 21Vianet, and Azure Government; production
workloads should use the stable version. Control-plane versions before
`2026-02-01` retire on February 27, 2027, and preview versions other than
`2026-04-01-preview` are deprecated with 90 days' notice; data-plane APIs are
unaffected.

### Control-plane client upgrade floor (key-vault-api-and-access-control)

Management clients must move to API-compatible releases, including
`Azure.ResourceManager.KeyVault` 1.4.0 or later for .NET, `armkeyvault/v2`
for Go, and the latest `@azure/arm-keyvault`, `azure-mgmt-keyvault`, or
`azure-resourcemanager-keyvault` for JavaScript, Python, or Java. Older
clients stop working when their API versions retire, and Cloud Shell always
uses the latest API version, so its scripts must already be compatible.

### Explicitly retain access policies (key-vault-api-and-access-control)

Access policies remain supported, but new vaults using the new API must set
`enableRbacAuthorization` to `false`; the latest CLI exposes the same choice
through an explicit flag.

```bash
az keyvault create --name "$vault_name" --resource-group "$resource_group" \
  --enable-rbac-authorization false
```

### Permissions required to change access models (key-vault-api-and-access-control)

Changing the property requires `Microsoft.KeyVault/vaults/write`. The portal
also requires `Microsoft.Authorization/roleAssignments/write` so an operator
can grant Key Vault RBAC roles after the switch and avoid a lockout.

### Private endpoint limits are enforced (key-vault-api-and-access-control)

Key Vault now enforces its per-vault private-endpoint limits. Vaults over the
limit must reduce their endpoint count or obtain an exception through support.

### RBAC becomes the create-time default (key-vault-api-and-access-control)

For vaults created through API version `2026-02-01` or later, omitting
`enableRbacAuthorization` now means `true`. This applies only to creation:
updating an existing vault with the new API does not change its access model,
and an existing `null` value continues to mean access policies.

## Managed identities and federation

### Federated-identity claims matching (2.74.0)

`az identity federated-credential create` and `update` now support claims
matching expressions.

### Legacy managed-identity login state removed (2.68.0)

Azure CLI no longer supports old-style managed-identity accounts created by
Azure CLI 2.0.50 or earlier. After upgrading such an installation, recreate
the account state by running `az login --identity` again.

### Managed-identity assignment restrictions (2.88.0)

`az identity create --resource-restriction` configures identity-assignment
restrictions.

### Managed-identity isolation scope (2.82.0)

`az identity create --isolation-scope` sets the isolation scope on a new
managed identity.

### Managed-identity login argument migration (2.69.0)

Passing a managed-identity ID to `az login --username` is deprecated. Use
`--client-id`, `--object-id`, or `--resource-id` instead before the old form
is removed.

### Managed-identity login migration enforced (2.73.0)

`az login --username` now rejects user-assigned managed-identity IDs; the
explicit identity flags documented in 2.69.0 are now mandatory.

### Managed-identity login without machine-FQDN lookup (2.83.0)

For managed-identity authentication, `az login` no longer retrieves the
machine FQDN, avoiding hangs or errors caused by a misconfigured network.

## Microsoft Entra, Graph, and mandatory MFA

### App manifests now use the Microsoft Graph shape (entra-authentication-and-graph)

Since January 7, 2025, the Entra admin center can no longer view, save, upload,
or download Azure AD Graph-format manifests on the App registrations manifest
page. Apps registered with a personal Microsoft account remain an exception;
source-controlled manifests for other apps must use the Microsoft Graph shape.

Important conversions include
`accessTokenAcceptedVersion` to `api.requestedAccessTokenVersion`,
`oauth2Permissions` to `api.oauth2PermissionScopes`, and
`acceptMappedClaims`, `knownClientApplications`, and
`preAuthorizedApplications` to same-named properties under `api`.
`oauth2AllowIdTokenImplicitFlow` and `oauth2AllowImplicitFlow` become
`web.implicitGrantSettings.enableIdTokenIssuance` and
`enableAccessTokenIssuance`; `replyUrlsWithType` splits into platform-specific
`redirectUris` under `web`, `spa`, or `publicClient`.

```json
{
  "displayName": "example",
  "api": {"requestedAccessTokenVersion": 2, "oauth2PermissionScopes": []},
  "web": {
    "redirectUris": ["https://example.test/callback"],
    "implicitGrantSettings": {
      "enableIdTokenIssuance": true, "enableAccessTokenIssuance": false
    }
  }
}
```

Also rename `allowPublicClient` to `isFallbackPublicClient`,
`informationalUrls` to `info`, and `name` to `displayName`; move `logoUrl`
under `info`, `logoutUrl` under `web`, and `signInUrl` to `web.homePageUrl`.
`errorUrl` is removed. `replyUrlsWithType` identifies the old format, whereas
`implicitGrantSettings` identifies the Microsoft Graph format.

### Azure AD Graph has reached full retirement (entra-authentication-and-graph)

Azure AD Graph was fully retired on August 31, 2025. New applications created
after August 31, 2024, and all applications from February 1, 2025, needed an
explicit extended-access opt-in; that escape hatch ended with retirement, so
remaining callers must migrate to Microsoft Graph.

### Mandatory MFA is enforced at Azure Resource Manager (entra-authentication-and-graph)

Phase 1 began in October 2024 for all CRUD operations in the Azure, Entra, and
Intune portals, with the Microsoft 365 admin center following in February
2025. Phase 2 began rolling out on October 1, 2025 for create, update, and
delete operations through Azure CLI, Azure PowerShell, the Azure mobile app,
IaC tools, Azure SDKs, and control-plane REST APIs; read operations don't
require MFA.

Phase 2 is enforced server-side for requests to
`https://management.azure.com`, regardless of client, and generally doesn't
cover Microsoft Graph APIs. It currently applies only to public Azure, not US
Government or other sovereign clouds. A user who signed in without MFA can
still read, but a write returns a claims challenge; use Azure CLI 2.76 or
Azure PowerShell 14.3 or later for the best challenge-handling compatibility.

### MSAL username-password APIs cannot satisfy mandatory MFA (entra-authentication-and-graph)

ROPC authentication fails when MFA is required. Public-client username/password
APIs were deprecated in MSAL for .NET 4.74.0, Go 1.6.0, Java 1.24.0, and
Python 1.35.0; the Node.js public and confidential
`acquireTokenByUsernamePassword` APIs were deprecated in 3.2.3. Confidential
username/password APIs that remain available still can't complete an MFA
challenge and must be replaced for affected user sign-ins.

### User accounts cannot bypass the platform MFA requirement (entra-authentication-and-graph)

Enforcement covers every user identity, including emergency-access accounts,
guests, test tenants, role-eligible users, and users excluded by Conditional
Access. Managed identities and service principals are outside both phases, so
automation using a user service account should migrate to a workload identity;
emergency accounts should use a passkey or certificate-based MFA.

External MFA can satisfy the requirement, but the legacy Conditional Access
custom-controls preview can't. A federated identity provider that performs MFA
must send an MFA assertion such as the `multipleauthn` claim to Entra ID.
