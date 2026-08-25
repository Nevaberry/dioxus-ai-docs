# GitLab Upgrade Planning

## Include every required GitLab 19 upgrade stop

Required GitLab 19 upgrade stops are `19.2`, `19.5`, `19.8`, and `19.11`.
Review the notes for every release between the current and target versions,
including any notes specific to the installation method.

## Avoid losing self-hosted Duo endpoints

A direct Linux package upgrade to 19.2.0 can clear the local AI Gateway and
Duo Agent Platform service URLs and reset related settings. Upgrade directly
to 19.2.1 or later.

If 19.2.0 has already caused the problem, restore the service endpoints under
**Admin area** > **GitLab Duo** > **Configuration** > **Service endpoints**.

## Handle the registry metadata database default

For existing Linux package and self-compiled installations without an explicit
`registry['database']['enabled']` setting, GitLab 19.0 defaults the container
registry metadata database to `prefer` mode. This falls back to legacy
filesystem metadata when data has not been imported.

In 19.0.0 and 19.0.1, this behavior can make `/gitlab/v1/` routes return HTTP
500 even though `/v2/` image pushes and pulls continue to work. Temporarily
disable the database, reconfigure and restart the registry, then remove the
override after upgrading to 19.0.2 or later:

```ruby
registry['database'] = {
  'enabled' => false
}
```

## Migrate container registry storage to `s3_v2`

GitLab 19.0 removes the legacy AWS SDK v1 `s3` driver and aliases it to
`s3_v2`. For non-AWS S3-compatible storage, `regionendpoint` must be a complete
URI. Backends that reject enhanced upload checksums require
`checksum_disabled`.

Deletion still sends CRC32. The object-storage backend must support that
operation; there is no GitLab configuration workaround for deletion.

```ruby
registry['storage'] = {
  's3_v2' => {
    'accesskey' => '<your-access-key>',
    'secretkey' => '<your-secret-key>',
    'bucket' => '<your-bucket>',
    'region' => '<your-region>',
    'regionendpoint' => 'https://storage.example.com',
    'pathstyle' => true,
    'checksum_disabled' => true
  }
}
```

## Upgrade PostgreSQL before GitLab 19

GitLab 19.0 requires PostgreSQL 17 for every installation method. Upgrade the
packaged PostgreSQL 16 server or an external PostgreSQL deployment before
installing GitLab 19.

## Repair Geo OCI image-index replication

Geo secondaries on 19.0.0 and 19.0.1 can silently omit OCI image-index tags,
including multi-architecture images and BuildKit cache tags. Upgrade both
sites to 19.0.2 or later.

Existing repositories recover during verification, which can take up to the
default 90-day interval. To repair them immediately, manually resync their
container repositories.

## Migrate off Ubuntu 20.04 packages

GitLab 18.11 is the final release with Linux packages for Ubuntu 20.04. Move
to Ubuntu 22.04 or another supported operating system before upgrading to
GitLab 19.

## Replace external Redis 6

GitLab 19.0 removes Redis 6 support. Migrate external deployments to Redis 7.0
or later or Valkey 7.2 before upgrading. The Redis bundled with the Linux
package is already version 7 and is unaffected.

## Remove bundled Mattermost and its configuration

GitLab 19.0 removes Mattermost from the Linux package. Move users of the
bundled service to standalone Mattermost. Remove or comment out every
`mattermost[...]` key in `/etc/gitlab/gitlab.rb` before upgrading, or
`gitlab-ctl reconfigure` aborts.

Do not rely on `gitlab-ctl check-config --version 19.0.x` to find this problem;
it does not detect the obsolete keys.

## Move SUSE Linux package installations to Docker

GitLab 18.11 is the final release providing Linux packages for openSUSE Leap
15.6, SLES 12.5, and SLES 15.6. Installations that must remain on SUSE need to
migrate to a Docker deployment for GitLab 19.

## Externalize Spamcheck

GitLab 19.0 removes bundled Spamcheck from both the Linux package and Helm
chart. Deploy it separately, such as with Docker. No data migration is
required.

## Prepare Helm upgrades for Envoy Gateway

The GitLab 19.0 Helm chart defaults to Gateway API with Envoy Gateway instead
of NGINX Ingress. Bundled NGINX Ingress can be explicitly re-enabled until its
proposed removal in GitLab 20.0.

Externally managed Ingress or Gateway API controllers and Linux package NGINX
are unaffected.

## Externalize Helm chart data services

GitLab 19.0 removes the bundled Bitnami PostgreSQL, Bitnami Redis, and MinIO
charts from the GitLab Helm chart and Operator without replacements. Configure
external services before upgrading an installation that used these
proof-of-concept components.

## Clean orphaned agent directories from RPM installations

RPM installations of GitLab 19.0.0–19.0.2 and 19.1.0 can leave `.agents` and
`.claude` under `/opt/gitlab/embedded/service/gitlab-rails/` after an upgrade
because RPM does not remove nonempty directories it no longer owns.

After reaching 19.0.3, 19.1.1, or 19.2 and later, check for and manually remove
these exact directories. DEB installations are unaffected.
