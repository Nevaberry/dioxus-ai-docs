# Services, Data Stores, and Administration

## Web and proxy servers

### Apache HTTP Server

Apache 2.4.62 in Ubuntu 24.10 adds SHA-2 password support to `htpasswd`, a third
`ProxyRemote` argument for Basic-auth credentials, and PKCS#11 certificate and
key loading in `mod_ssl`. CA certificates found through
`SSLProxyMachineCertificateFile` or `SSLProxyMachineCertificatePath` are treated
as chain certificates.

In Ubuntu 25.04, `mod_authnz_ldap` adds `ldap-search` authorization using
arbitrary expressions. `mod_ssl` again allows PKCS#11 ENGINE keys without
`SSLCryptoDevice`. Experimental `mod_tls` is no longer packaged with Apache and
must be obtained separately if still required.

Apache 2.4.64 in Ubuntu 25.10 adds systemd socket activation through
`mod_systemd`, the `H2MaxHeaderBlockLen` response-header size limit, and reuse of
`ProxyRemote` connections by `mod_proxy`.

### Nginx TLS material

Nginx 1.28 in Ubuntu 25.10 caches certificates, private keys, and CRLs during
startup or reconfiguration. Reconfigure Nginx after changing TLS material; do
not assume those files are reread for every connection.

## Malware scanning

ClamAV 1.4 in Ubuntu 24.10 adds ALZ, LHA/LZH, OneNote, and UDF scanning plus
image extraction from HTML CSS. It adds controls for image fuzzy hashing and
clean-cache size through `--cache-size`. Freshclam can authenticate to private
mirrors with a client certificate and key, and startup can be configured to abort
when the signature database is too old.

## Redis and Valkey

Installing `valkey-redis-compat` in Ubuntu 24.10 attempts to migrate Redis data
and configuration, creates `/etc/valkey/REDIS_MIGRATION`, and leaves services
stopped for review. Validate the migration before removing the marker; its
removal permits Valkey services to start.

Ubuntu 25.10 removes `valkey-redis-compat` because Redis has moved to 8.0 and
Valkey is no longer treated as a drop-in replacement. Complete any Redis-to-
Valkey switch before the release upgrade.

## Samba

In Ubuntu 24.10, most modules from `samba-vfs-modules` move into `samba`, while
Ceph support moves to `samba-vfs-ceph`; the old package is transitional. The
GlusterFS module moves from transitional `samba-vfs-modules-extra` to
`samba-vfs-glusterfs`.

Samba 4.21 in Ubuntu 25.04 makes some formerly public libraries private and no
longer provides `python3-samba` or `samba-tool` on i386. Before upgrading an
Active Directory domain controller assembled without `samba-ad-dc`, install
that package or required components will be missing after upgrade.

Samba 4.22 in Ubuntu 25.10 adds SMB3 directory leases, Netlogon Ping over LDAP
or LDAPS, and experimental Himmelblaud authentication. Remove the deleted
`nmbd proxy logon`, `cldap port`, and `fruit:posix_rename` options from existing
configuration.

## Databases and application runtimes

### MySQL and backup tooling

Ubuntu 25.04 moves MySQL Server, MySQL Shell, and Percona XtraBackup from the
8.0 line to 8.4 LTS. XtraBackup supports the `keyring_vault` component. MySQL
Server is no longer built for 32-bit systems, although the 8.4 client and client
library remain available there.

### PHP and Django

Ubuntu 25.04 moves PHP to 8.4, including property hooks, asymmetric visibility,
and the updated DOM API.

Ubuntu 25.10 moves the packaged Django from 4.2 to the 5.2 LTS series and updates
distribution-provided Django middleware for that version.

### PostgreSQL

Ubuntu 25.04 moves PostgreSQL to 17, which adds SQL/JSON constructors,
`JSON_TABLE()`, and `sslnegotiation=direct` for a direct TLS handshake.

The Ubuntu 25.10 PostgreSQL 17.6 update does not require dump and restore. After
updating, recreate affected self-referential foreign-key constraints on
partitioned tables and reindex any `BRIN numeric_minmax_multi_ops` indexes.

## Mail services

Dovecot 2.4 in Ubuntu 25.10 renames parameters and substantially changes
configuration syntax. Convert and carefully review a Dovecot 2.3 configuration
instead of restarting unchanged. Dovecot adds Argon2 passwords,
SCRAM-SHA-1/SHA-256 SASL, and X25519/X448, but is no longer natively installable
on i386 or armhf.

## Backup and high availability

### Bacula coordinated upgrade

Ubuntu 25.10 moves Bacula from 13.0.4 to 15.0.3. Upgrade Director and Storage
daemons together; older File daemons and `BB02` volumes remain supported.
Migrate the catalog schema—`dbconfig-common` does this automatically where it is
in use. Newly written volumes use `BB03`.

### Cluster administration migration

Ubuntu's server-administration guidance provides a dedicated procedure for
migrating high-availability systems managed with `crmsh` to `pcs`. Treat it as
an administration-tool migration, not a drop-in command substitution.

### RabbitMQ release hops

During an Ubuntu 25.04 upgrade, ensure RabbitMQ does not cross an unsupported
version hop made invalid by feature flags. Plan supported intermediate versions
instead of relying on the distribution upgrade alone.

## Monitoring and diagnostics

Monitoring Plugins 2.4 in Ubuntu 25.04 adds HAProxy protocol support to
`check_curl`, threshold-free operation to `check_swap`, IPv6 to `check_ircd`,
percent-used output to `check_nwstat`, and real-power plus additional-alarm
output to `check_ups`.

The `sosreport` package is renamed to `sos`. The `sosreport` and `sos-collector`
commands are scheduled for removal after a short transition; use the `sos`
command family. `sos upload` can send an archive or another file to a supported
vendor.

Sos 4.10 in Ubuntu 25.10 creates temporary working data under `/var/tmp` rather
than `/tmp`. Size and clean up the correct filesystem.
