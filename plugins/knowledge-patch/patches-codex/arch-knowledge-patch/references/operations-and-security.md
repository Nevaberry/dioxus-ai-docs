# Operations and Security

Covered batches: `2025-q3-operations` and `unversioned`.

## Arch service outages

### Use configured package mirrors

If `archlinux.org` is unavailable, use mirrors already listed by `pacman-mirrorlist` instead of depending on the unavailable mirror-list endpoint.

Obtain installation images from an Arch mirror, and continue to verify image integrity and signatures.

### Use service-specific fallbacks

For AUR downtime, retrieve a package from Arch's GitHub mirror:

```sh
git clone --branch <package_name> --single-branch https://github.com/archlinux/aur.git <package_name>
```

For wiki downtime, use recent snapshots from `arch-wiki-docs` or `arch-wiki-lite`.

During the documented hosting mitigation, treat one initial connection reset as a possible result of TCP SYN authentication and retry the request once.

## AUR incident response

### Audit every package update

The AUR is experiencing a high volume of malicious package adoptions and updates. Before updating any AUR package:

1. Review every change to its `PKGBUILD`.
2. Review every change to its install scripts.
3. Stop when a new maintainer, source, download, or install action is suspicious.
4. Report suspicious commits for packages in use to Arch staff through the `aur-general` mailing list.

Do not delegate trust to an AUR helper during this incident; inspect the source changes that the helper proposes to build.
