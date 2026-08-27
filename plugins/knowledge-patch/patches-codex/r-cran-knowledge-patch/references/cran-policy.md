# CRAN Package Policy

This topic reference is attributed to `cran-policy`.

## Complete redistributable source

- An open-source package must provide source, or material easily converted
  back to source, for every component.
- This requirement includes generated `configure` files, PDF documentation,
  and Java bytecode.
- Java sources should be in a top-level `java` directory. If they are not,
  that directory should explain how to obtain them.
- Direct and indirect dependencies cannot restrict users or usage.
- The package license must permit CRAN to distribute it in perpetuity.
- Highlight any license change when submitting the package.

## Persistent package names

- A proposed name must not conflict case-insensitively with any current or
  past CRAN package or any current Bioconductor package.
- CRAN package names persist and ordinarily cannot be changed.
- A takeover requires the previous maintainer's written agreement unless the
  package is formally orphaned.

## Repository and orphan dependency constraints

- Strong dependencies listed in `Depends`, `Imports`, or `LinkingTo` should
  come from CRAN or the Bioconductor software repository.
- For a nonstandard `Suggests` or `Enhances` dependency, provide its
  repository URL in `Additional_repositories` or give other access
  instructions in `Description`.
- Use such a dependency conditionally when it is not readily installable on
  major platforms.
- An orphaned CRAN package should not be a direct or indirect strong
  dependency.
- Conditional use of an orphaned package from `Suggests` is allowed but
  discouraged.

## External libraries and installation downloads

- Installation should first look for a suitable installed external library.
- If none is suitable, preferably compile bundled source.
- Any downloaded source must have a fixed version.
- Downloading precompiled software is a last resort and requires agreement
  from the CRAN team.
- Windows and macOS builds must use static libraries.
- Installation and startup downloads must be secure.
- Set a sufficiently large timeout when downloading more than a few
  megabytes.

## Shared Internet resources

- An Internet-dependent package must fail informatively if a resource is
  unavailable or has changed.
- That failure must not produce an `R CMD check` warning or error.
- Minimize use of external resources because multiple packages may share a
  service.
- In particular, avoid rate-limit responses such as HTTP 429 and 403.

## Compatibility with released dependencies

- The CRAN version of a package should work with current CRAN and
  Bioconductor releases.
- Do not anticipate or recommend development versions.
- A package that errors under `R CMD check` when a new R *x.y.0* is released
  is liable to archival unless the maintainer sets a firm update deadline
  and meets it.

## Disruptive and API changes

- Changes that significantly disrupt other packages require agreement with
  CRAN maintainers well before publicity.
- A new package must not provide a back-compatibility version of a package
  that is already available.
- Before an API-changing update, notify affected reverse-dependency
  maintainers.
- Allow at least two weeks, and ideally longer, for those maintainers to
  update.

## Update and resubmission timing

- An update to a published package requires a higher version.
- Increasing the version after each unsuccessful submission is preferred.
- Established packages should normally be updated no more often than every
  one to two months.
- Do not submit a replacement while another submission is pending.
- After publication, wait until the CRAN check page has finished updating
  before submitting corrections. This can take at least 48 hours.
- For `macos-arm64` or `M1mac` issues, use macbuilder first.
