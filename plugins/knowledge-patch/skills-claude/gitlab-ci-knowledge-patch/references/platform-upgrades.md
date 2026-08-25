# GitLab Platform Upgrade Guidance

## Plan required GitLab 19 upgrade stops

Required GitLab 19 upgrade stops are `19.2`, `19.5`, `19.8`, and `19.11`. Stop at
each one that lies between the current and target versions. Review the notes for
every intervening version, including notes specific to Linux packages, Helm,
Operator, Docker, or self-compiled installations as applicable.

## Protect self-hosted Duo endpoints during the 19.2 upgrade

A direct Linux-package upgrade to `19.2.0` can clear local AI Gateway and Duo Agent
Platform service URLs and reset related settings. Upgrade to `19.2.1` or later.

If `19.2.0` already caused the loss, restore the endpoints under **Admin area** >
**GitLab Duo** > **Configuration** > **Service endpoints**.

## Handle the registry metadata database default

For existing Linux-package and self-compiled installations without an explicit
`registry['database']['enabled']`, GitLab 19.0 changes the registry metadata database
to `prefer` mode. That mode falls back to legacy filesystem metadata until data has
been imported.

In `19.0.0` and `19.0.1`, the mode can cause `/gitlab/v1/` routes to return HTTP 500,
although `/v2/` image pushes and pulls continue to work. Temporarily disable the
database, reconfigure, and restart the registry:

```ruby
registry['database'] = {
  'enabled' => false
}
```

After upgrading to `19.0.2` or later, remove the temporary override.

## Migrate registry object storage to `s3_v2`

GitLab 19.0 removes the legacy AWS SDK v1 `s3` registry driver and aliases `s3` to
`s3_v2`. Configure `s3_v2` explicitly:

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

For non-AWS S3-compatible storage, `regionendpoint` must be a complete URI. Set
`checksum_disabled` when the backend rejects enhanced upload checksums. Registry
deletion still sends CRC32; a backend that cannot accept it requires a backend-side
change because GitLab has no configuration workaround.

## Upgrade PostgreSQL before GitLab 19

GitLab 19.0 requires PostgreSQL 17 for every installation method. Upgrade a packaged
PostgreSQL 16 server or an external PostgreSQL deployment before installing GitLab
19.

## Repair Geo OCI image-index replication

Geo secondaries on `19.0.0` and `19.0.1` can silently omit OCI image-index tags,
including multi-architecture image tags and BuildKit cache tags. Upgrade both Geo
sites to `19.0.2` or later.

Existing repositories recover during verification, which can take as long as the
default 90-day interval. Manually resync affected container repositories when
immediate repair is required.

## Leave unsupported Linux package platforms

GitLab 18.11 is the final Linux-package release for Ubuntu 20.04. Move those hosts
to Ubuntu 22.04 or another supported operating system before upgrading to GitLab 19.

GitLab 18.11 is also the final package release for openSUSE Leap 15.6, SLES 12.5,
and SLES 15.6. Installations that must remain on SUSE must move to a Docker
deployment for GitLab 19.

## Replace external Redis 6

GitLab 19.0 removes Redis 6 support. Move external deployments to Redis 7.0 or later
or to Valkey 7.2 before the GitLab upgrade. The Redis bundled with the Linux package
is already version 7 and does not require this migration.

## Remove bundled Mattermost configuration

GitLab 19.0 removes Mattermost from the Linux package. Migrate users of the bundled
service to standalone Mattermost, then remove or comment out every
`mattermost[...]` key in `/etc/gitlab/gitlab.rb` before upgrading. If any key
remains, `gitlab-ctl reconfigure` aborts. `gitlab-ctl check-config --version 19.0.x`
does not detect this problem.

## Externalize Spamcheck

GitLab 19.0 removes bundled Spamcheck from both the Linux package and Helm chart.
Deploy it separately, for example with Docker, before relying on it after the
upgrade. No Spamcheck data migration is required.

## Prepare Helm ingress for Envoy Gateway

The GitLab 19.0 Helm chart defaults to Gateway API with Envoy Gateway rather than
NGINX Ingress. The bundled NGINX Ingress can be explicitly re-enabled until its
proposed removal in GitLab 20.0. Externally managed Ingress controllers, externally
managed Gateway API controllers, and Linux-package NGINX are unaffected.

## Externalize Helm chart data services

GitLab 19.0 removes the bundled Bitnami PostgreSQL, Bitnami Redis, and MinIO charts
from the GitLab Helm chart and Operator, without replacements. Configure external
services before upgrading an installation that used these proof-of-concept
components.

## Clean orphaned agent directories on RPM systems

RPM installations of `19.0.0` through `19.0.2` and `19.1.0` can leave nonempty
`.agents` and `.claude` directories under
`/opt/gitlab/embedded/service/gitlab-rails/` because RPM no longer owns them.

After reaching `19.0.3`, `19.1.1`, or `19.2` and later, check for and manually
remove exactly those two directories. DEB installations are unaffected. Inspect
their contents before removal so unrelated administrator-created data is not lost.
