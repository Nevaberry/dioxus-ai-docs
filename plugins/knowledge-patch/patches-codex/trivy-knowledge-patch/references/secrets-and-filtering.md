# Secrets and Filtering

## Secret inspection modes

### Client/server analysis

In client/server mode, the configuration analyzer performs secret inspection
(since 0.60.0). Do not assume secret scanning is restricted to a local
analysis path.

### Input safety and locations

Secret scanning validates UTF-8 before protobuf marshaling and reports corrected
line numbers for multiline secrets (since 0.65.0).

### Python metadata directories

Secret scanning ignores `.dist-info` directories (since 0.62.0).

## Detector quality and new rules

### Meaningful matches and examples

Secret matches must have meaningful length, and example strings can remain
unflagged (since 0.63.0). This reduces low-information and intentional-example
findings.

### Token and framework patterns

Secret scanning recognizes the Symfony default secret key and applies improved
word-boundary handling to Hugging Face tokens (since 0.69.0).

It adds Azure secret rules and detects passwords and passphrases in Maven
`settings.xml` and `settings-security.xml` (since 0.71.0).

Rules also recognize OpenAI API secrets and the stateless form of GitHub
App installation tokens (since 0.72.0).

## Secret-scan exclusions

Skipped folders, files, and file extensions are configurable (since 0.71.0).
The secret scanner skips its own configuration file, preventing detector
configuration from becoming a finding source.

## Misconfiguration ignores

### Inline ignores

Inline-comment ignores work when scanning Dockerfiles and Helm content (since
0.59.0).

### Chart paths

Ignore rules retain chart-relative path semantics when a chart lives in a
subdirectory (since 0.66.0).

### Case and aliases

Misconfiguration ignore IDs are matched case-insensitively (since 0.71.0).
When `.trivyignore` names a check alias, filtering suppresses the corresponding
check (since 0.70.0).

### Ignore-marker values

A value used as an ignore marker must be both known and non-null (since
0.68.0). Unknown or null expressions do not activate the ignore.

## Vulnerability and package filtering

### Image-history check selection

Image-history scanning does not run check `AVD-DS-0007` (since 0.60.0).

### Package-type filtering

License scanning respects the package-types option, so selecting package types
also filters license findings (since 0.65.0).

### Third-party operating-system packages

Debian packages are classified as third-party using maintainer metadata.
Distribution vulnerability matching skips third-party packages on Debian and
Ubuntu (since 0.69.0), and the common vulnerability path applies the same
third-party exclusion (since 0.70.0).

### Rego result filtering

Rego processing can ignore findings by type, and misconfiguration scanning
accepts a configurable Rego error limit (since 0.68.0).
