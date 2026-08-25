# Command-Line and Library Interfaces

## `projinfo`

`projinfo` displays whether an operation is time-dependent and installs a Bash
completion script (since 9.6.0). Use the time-dependence indication when
deciding whether coordinate epochs must be preserved.

The `-k crs` restriction is honored (since 9.7.1):

```sh
projinfo -k crs AUTHORITY:CODE
```

Requests limited to CRS objects no longer silently ignore that filter. Scripts
that worked around the old behavior should remove their own post-filter only
after verifying the installed command.

## Library Form of `projinfo`

`projinfo` functionality is exposed through the library and the installed
public header `projapps_lib.h` (since 9.8.0). This supports in-process use cases
that previously parsed subprocess output.

When adopting it:

- include only the installed public header;
- link using the installation’s corrected pkg-config metadata;
- preserve the calling application’s PROJ context and error policy; and
- do not assume command-line formatting is a stable interchange format.

## Direct Geodesic API

`proj_geod_direct()` performs a direct geodesic calculation with a `PJ` object
(since 9.7.0). It is useful when the application already owns the appropriate
PROJ object and wants a public direct-geodesic entry point.

Validate object suitability, units, longitude behavior, and failure reporting
in the same way as adjacent `PJ` operations.

## Object Cloning

`proj_clone()` carries `errorIfBestTransformationNotAvailable` and other source
flags to the clone (since 9.6.0). It also preserves `FORCE_OVER=YES` (since
9.7.1), so longitude-overrange behavior does not silently disappear.

For code that caches or clones operations:

1. Configure behavior on the source object.
2. Clone it in the intended context.
3. Exercise coordinates outside the conventional longitude range.
4. Exercise a case where the best transformation is unavailable.
5. Compare error state and pipeline behavior between original and clone.

Do not compensate for old clone behavior by setting flags twice unless support
for an affected older release is an explicit requirement.

## Context State After Downloads

After `proj_download_file()` downloads a file, caches associated with the file
are invalidated in the current context (since 9.6.0). A subsequent lookup in
that context can discover the new resource without retaining stale file state.

Scope matters: this guarantee names the current context. Coordinate cache
lifecycle explicitly across worker contexts or processes when a download is
shared externally.

## API Integration Checklist

- Check return values and context error state.
- Keep each `PJ` object associated with the intended lifecycle and context.
- Verify behavioral flags after cloning.
- Preserve coordinate epochs when `projinfo` reports time dependence.
- Prefer `projapps_lib.h` to private declarations.
- Treat CLI text as presentation, not a stable machine protocol.
- Retest linking with `proj.pc` from the installed package.
