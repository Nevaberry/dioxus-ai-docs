# Identity and Directory Services

Consult this reference for authselect, SSSD, IdM, Directory Server, Samba, Active Directory integration, certificates, passkeys, and identity migration.

## Contents

- [Authentication selection, SSSD, sudo, and login](#authentication-selection-sssd-sudo-and-login)
- [IdM deployment, ranges, certificates, and migration](#idm-deployment-ranges-certificates-and-migration)
- [Directory Server storage and administration](#directory-server-storage-and-administration)
- [Samba and Active Directory interoperability](#samba-and-active-directory-interoperability)

## Authentication selection, SSSD, sudo, and login

### Authselect ownership and defaults (10.0)

`authselect-libs` now owns `/etc/nsswitch.conf` and core PAM files, so authselect is required; on authselect-managed systems, subsequent calls overwrite out-of-band edits without prompting. Custom behavior belongs in a custom profile or requires `authselect opt-out`; the new `local` profile replaces `minimal` and is the install default because SSSD's files provider is removed.

### SSSD transport and privilege controls (10.0)

Dynamic DNS updates can use DoT through `dyndns_dns_over_tls` and the TLS certificate/key options; `ldap_pwmodify_mode=exop_force` attempts expired-password changes even with no grace logins. Use `sss_ssh_knownhosts` with OpenSSH `KnownHostsCommand`, and keep `sssd.conf` at `root:sssd` mode `0640` for the reduced-privilege service layout.

### Removed identity interfaces (10.0)

Kerberos RSA PKINIT is removed in favor of Diffie-Hellman/ECDH, and IdM no longer provides a NIS emulator. Directory Server drops BDB, while SSSD drops AD/IdM enumeration, its files provider, `ad_allow_remote_domain_local_groups`, and `reconnection_retries`; use the proxy provider where local-account integration is still needed.

### SSSD LDAP and smart-card behavior (10.1)

SSSD now scans every inserted PKCS #11 token for a matching smart-card certificate. `ldap_read_rootdse=authenticated` delays RootDSE reads until login and `never` disables them, avoiding anonymous LDAP binds; separately, realmd policy-kit rules now permit unprivileged host-keytab renewal.

### SSSD large-group caveat (10.1)

Active Directory groups above the default 1,500-value `MaxValRange` can produce incomplete SSSD membership lists; increase that AD policy limit when larger groups must be retrieved intact.

### IdM password-reset integrations (10.2)

IdM system accounts can reset passwords over LDAP without forcing a user password change; `ipasysaccount` creates them and `iparole` grants privileges, while automated `crond` and `systemd-user` sessions no longer clear faillock counters. Password policies add `--dcredit`, `--ucredit`, `--lcredit`, and `--ocredit`, where negative values require characters and positive values credit minimum length; these options are mutually exclusive with `--minclasses`.

### SSSD, adcli, and sudo interfaces (10.2)

`adcli delete-computer --recursive` removes an AD computer and child objects such as BitLocker metadata. Sudo 1.9.17p2 adds regex sudoers entries, `log_subcmds`, `intercept`, compact JSON logging, `sudo -N`, granular I/O logging switches, and UTF-8 LDAP identities.

### Identity and desktop previews (10.2)

The preview generic SSSD IdP reads users and groups from Keycloak or Entra ID and authenticates with OAuth 2.0 Device Authorization Grant. `authselect`'s `with-switchable-auth` enables preview selection among EIdP, FIDO2 passkey, and smart-card login in GDM; IdM's preview modern UI is at `/ipa/modern-ui`, and Mutter 49 exposes a preview HDR switch.

### Removed command and identity interfaces (10.2)

`vi` now always starts `vim-minimal` even when `vim-enhanced` is installed; use `vim` explicitly for the full editor. SSSD removes the nonfunctional `ipa_enable_dns_sites` option.


## IdM deployment, ranges, certificates, and migration

### IdM range and certificate lifecycle (10.0)

`ipa-idrange-fix` finds users and groups outside local ID ranges and proposes new ranges, excluding IDs below 1000 by default. New replicas enable RSNv3 random serials and delete expired certificates after a default 30-day retention; IdM ACME is supported but must be enabled deployment-wide, and an existing CA/KRA cannot be migrated into the newly supported HSM setup.

### IdM and Directory Server caveats (10.0)

Integrated IdM DNS is not usable in this release: `ipa-server-dns` installation and `--setup-dns` configuration fail, and DNSSEC is broken by the PKCS #11 provider transition. SSSD's daily `adcli` machine-password renewal also fails, so renew it independently; use `dsconf ... config delete` instead of `ldapmodify` to delete one `cn=config` value.

### Extended IdM UID range (10.1)

IdM can use the upper half of the 32-bit POSIX ID space only by disabling SubID with `ipa config-mod --addattr ipaconfigstring=SubID:Disable`, removing subordinate ranges, running `ipa-server-upgrade`, and creating a local range with RID bases. This is possible only before any subordinate IDs have been allocated and sacrifices the SubID feature.

### IdM migration, HSM, and ACME support (10.1)

`ipa-migrate` and HSM-backed IdM CA/KRA deployments move from preview to full support, although an existing CA or KRA still cannot be migrated onto an HSM. The IdM ACME server now accepts ES256 JWK signatures, enabling clients such as Caddy.

### IdM health and Ansible interfaces (10.1)

`ipa-healthcheck` warns 28 days before user-provided HTTP, Directory Server, or PKINIT certificates expire, and flags the high-load `krbLastSuccessfulAuth` setting. The RPM collection accepts playbooks written for the `redhat.rhel_idm` namespace, while preview DoT automation adds `ipaserver_dns_over_tls`, `ipareplica_dns_over_tls`, `dot_forwarder`, certificate/key, and `dns_policy` variables.

### IdM client targeting and passkeys (10.2)

`ipa-client-automount --domain DOMAIN` overrides DNS discovery, and `ipa-certupdate --force-server SERVER_FQDN` refreshes trust from a non-default server. Ansible modules for config, hosts, services, and users accept `passkey` authentication, while `ipapasskeyconfig` controls whether a passkey requires user verification.

### IdM HSM and proxy controls (10.2)

HSM-backed installations now generate Lightweight CA certificates and `TOKEN:lwca` private keys on the HSM. Directory Server's `nsslapd-haproxy-trusted-ip` accepts mixed individual addresses and CIDR ranges, and IdM trusts are supported with Windows Server 2025 but no longer with Windows Server 2012 R2.

### IdM migration caveat (10.2)

`ipa-migrate` does not copy user or ID-override SSH public keys. Export them with `ipa user-find --all` or `ldapsearch` and restore them with `ipa user-mod --sshpubkey`.


## Directory Server storage and administration

### Directory Server moves to LMDB (10.0)

New 389 Directory Server instances use LMDB only; BDB instances must be exported/imported or replicated into a new instance. Tune `nsslapd-mdb-max-size`, `nsslapd-mdb-max-readers`, and `nsslapd-mdb-max-dbs`; PBKDF2 storage schemes now default to 100,000 iterations and can be changed with `dsconf ... set-num-iterations`.

### Directory Server administration (10.1)

`dsconf plugin attr-uniq set --exclude-subtree DN` can exclude subtrees from uniqueness checks, and `uniqueness-attribute-name: ATTRIBUTE:MATCHING-RULE:` can override comparison semantics. Access and error logs support JSON through `dsconf INSTANCE logging access|error set log-format json`, while `dsidm ... list --full-dn` emits complete DNs.

### Directory Server cache and dynamic groups (10.2)

`nsslapd-cache-pinned-entries=N` pins the largest group entries in a backend cache and defaults to zero. Dynamic groups are disabled by default and are enabled with `nsslapd-dynamic-lists-enabled`, with configurable object class, LDAP-URL, and result attributes defaulting to `groupOfURLs`, `memberUrl`, and `member`.

### Online directory certificates and PQ TLS (10.2)

After replacing a Directory Server certificate, run `dsconf INSTANCE config refresh-certs` to use it for new connections without restarting; existing sessions remain open unless clients react to a CA change. Directory Server and Certificate System now accept ML-DSA-44, -65, and -87 certificates and signatures.

### Directory replication and import administration (10.2)

`dsconf INSTANCE repl-conflict delete-all SUFFIX` removes all replication conflicts, and LDIF import validates the expected suffix before erasing the existing backend. MemberOf adds `memberOfSpecificGroupFilter`, `memberOfExcludeSpecificGroupFilter`, and `memberOfSpecificGroupOC` to scope processing to selected groups.

### Directory diagnostics and LMDB CLI behavior (10.2)

`dscreate` and `dsconf ... --mdb-max-size` now accept `k`, `m`, `g`, and `t` suffixes; `dsctl db2index --attr` requires a backend argument instead of silently indexing everything. Access-log `notes=N` identifies asynchronous searches and `notes=B` those blocking new operations, suggesting `nsslapd-maxthreadsperconn` may need adjustment.


## Samba and Active Directory interoperability

### Samba 4.22 compatibility (10.1)

Samba adds SMB3 directory leases and can query domain controllers over LDAP or LDAPS by setting `client netlogon ping protocol` instead of relying on CLDAP. It removes `nmbd_proxy_logon`, `cldap port`, and `fruit:posix_rename`; back up TDB files before first start and validate the upgraded configuration with `testparm`.

### Samba 4.23 operating changes (10.2)

SMB3 UNIX extensions are enabled by default; experimental SMB-over-QUIC is selected through `client smb transports` or `server smb transports`. `smb_prometheus_endpoint` exports metrics, and `samba-tool domain backup --no-secrets` strips BitLocker recovery data, KDS root keys, and other confidential attributes.

