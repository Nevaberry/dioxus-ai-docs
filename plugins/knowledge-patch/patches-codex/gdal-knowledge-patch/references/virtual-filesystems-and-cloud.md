# Virtual Filesystems and Cloud

## S3 and AWS authentication

- **IAM Identity Center (3.10.1).** `/vsis3/` supports AWS Single Sign-On,
  now named AWS IAM Identity Center.

- **SSO cache, region, and path options (3.11.4).** AWS SSO uses the correct
  cache-file location and region parameter. `/vsis3/` directory reads honor
  path-specific options.

- **EC2 credentials (3.11.5).** New `/vsis3/` connections using EC2
  credentials no longer enter the WebIdentity authentication path.

- **Directory buckets and credential processes (3.12.0).** `/vsis3/` supports
  S3 directory buckets and AWS `credential_process` authentication.

- **Endpoint spelling (3.11.0).** `AWS_S3_ENDPOINT` can include an
  `http://` or `https://` prefix.

## Curl-backed HTTP behavior

- **Retry SSL connection timeouts (3.10.3).** The CPL HTTP layer retries
  errors reported as `SSL connection timeout`.

- **Path-specific request controls (3.11.0).** `VSICURL_QUERY_STRING` is a
  path-specific option. `/vsicurl?` URLs accept
  `header.<key>=<value>`. `GDAL_HTTP_MAX_CACHED_CONNECTIONS` and
  `GDAL_HTTP_MAX_TOTAL_CONNECTIONS` bound connection caching.
  `CPL_VSIL_CURL_CACHE_SIZE` and `CPL_VSIL_CURL_CHUNK_SIZE` accept memory
  units.

- **Streaming redirects (3.11.0).** `/vsicurl_streaming/` follows HTTP 303
  redirects.

- **Redirect sizes and authorization (3.12.2).** `/vsicurl_streaming/`
  reports correct file sizes, and `/vsicurl/` handles HTTP 302 replies to
  `HEAD`. Authentication from the original URL is not sent to an S3-like
  redirect.

- **Missing `Content-Length` (3.12.4).** If an initial `HEAD` advertises
  `Accept-ranges: bytes` but has no `Content-Length`, `/vsicurl/` retries with
  a limited-range `GET`.

- **Redirect policy and retries (3.13.0).** Redirect-authorization policy can
  be path-specific. Multi-range reads retry HTTP 429 and 5xx responses.

- **Header-file and Nginx listing safety (3.13.2).** The `header_file` value
  in a `/vsicurl?` URL is limited to permitted filenames. File sizes are
  correct for Nginx autoindex listings produced with
  `autoindex_exact_size off`.

## Cache and path semantics

- **Credential-sensitive cache invalidation (3.10.3).** `/vsigs/` and
  `/vsiaz/` invalidate cached file and directory state when authentication
  parameters change.

- **Normalized cloud paths (3.12.0).** Cloud VSI paths squash `/./` and
  `/../` by default. Set `GDAL_HTTP_PATH_VERBATIM` to preserve those segments.

- **Post-close caching (3.12.0).** `VSIFOpenEx2L()` accepts `CACHE=ON/OFF` for
  `/vsicurl/`-style files.

- **Single-file timestamps (3.13.1).** `gdal vsi list` displays the
  last-modification timestamp when the target is a single file.

## Google, Azure, Swift, and WebHDFS

- **Bearer-token Google operations (3.11.1).** `/vsigs/` supports
  `UnlinkBatch()` and `GetFileMetadata()` when an OAuth2 bearer token is passed
  in `GDAL_HTTP_HEADERS`.

- **Forwarded HTTP options (3.11.1).** `/vsiswift/` forwards HTTP settings for
  listing. `/vsiwebhdfs/` forwards them for listing, deletion, and directory
  creation.

- **Unsigned Azure listing (3.11.4).** `/vsiaz/` `ReadDir()` works with
  `AZURE_NO_SIGN_REQUEST=YES`.

- **Google Cloud Run credentials (3.13.0).** `/vsigs/` recognizes Google
  Cloud Run for GCE authentication.

- **Azure token metadata (3.13.2).** Azure/ADLS handler option metadata
  includes `AZURE_STORAGE_ACCESS_TOKEN` and `AZURE_STORAGE_SAS_TOKEN`.

## Sync and archives

- **Single-file RAR reads (3.11.4).** `/vsirar/` no longer returns a negative
  read result for a single-file archive opened through a path such as
  `/vsirar/the.rar`.

- **Empty files in cloud sync (3.13.2).** Multithreaded `VSISync()` includes
  empty files in either synchronization direction with cloud storage.
