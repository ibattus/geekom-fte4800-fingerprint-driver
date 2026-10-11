# AUR package: focaltech-fte4800-geekom

This self-contained recipe is prepared for AUR submission. It is **not yet
published on AUR**. The proposed name was available when checked on 2026-10-11.
It targets the tested GEEKOM NX14CM SPI configuration rather than claiming
compatibility with every FTE4800 device.

## Build locally

From this directory:

```sh
makepkg --syncdeps
```

Unlike the older `packaging/arch` recipe, this directory does not require the
rest of the Git checkout at build time. It downloads a fixed, checksummed
GitHub source archive, a checksummed libfprint release archive, and the pinned
Microsoft driver archive. It verifies the extracted DLL's checksum separately.

Version `1.0.3-1` is a new package name for the source previously tested as
`focaltech-fte4800 1.0.3-5`. The private library, runtime paths, module name,
and DKMS package name are preserved. `provides` and `conflicts` handle the
older package names; `replaces` is deliberately omitted for this AUR variant.

The package runs all three libfprint core unit suites in `check()`. Install
headers for your actual kernel before installing the package so DKMS can
build the module. `linux-headers` is suggested for the standard Arch kernel;
LTS and custom kernels need their corresponding headers.

PAM policy is not changed by package installation. Use the examples in
`install/pam` after reviewing your local service files.

## Validation

On 2026-10-11, from a separate directory containing only the AUR recipe:

- All source archive and extracted DLL checksums passed.
- `makepkg --cleanbuild --force` completed successfully.
- All three libfprint core unit suites passed.
- The packaged kernel source compiled against the running kernel headers.
- Package contents use the expected DKMS source and private runtime paths.
- Namcap reported no errors for the PKGBUILD or built package. Its two
  remaining warnings concern `dkms` and `fprintd`, which are required for
  module builds and fingerprint authentication even though they are not
  linked ELF-library dependencies.

The local test build did not replace the installed working driver. A clean
chroot build has not been performed. Biometric performance and broader hardware
validation are described in the main README and SECURITY.md.

## Publish to AUR

AUR has separate accounts and authentication from GitHub. Register at
https://aur.archlinux.org/register/ and add an SSH public key in your account
settings. See the official submission instructions:
https://wiki.archlinux.org/title/AUR_submission_guidelines.

You can create a dedicated key interactively:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_aur -C AUR
cat ~/.ssh/id_ed25519_aur.pub
```

Upload the **public** key's text to AUR. Keep the private key local.
Then test authentication:

```sh
ssh -i ~/.ssh/id_ed25519_aur -o IdentitiesOnly=yes aur@aur.archlinux.org
```

A standalone local `master`-branch submission repository has been prepared on
the development machine at `~/Projects/aur/focaltech-fte4800-geekom`.
It contains only `PKGBUILD`, `.SRCINFO`, the `.install` file and `.gitignore`.
From that directory, once your AUR key is registered:

```sh
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_aur -o IdentitiesOnly=yes' git ls-remote origin
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_aur -o IdentitiesOnly=yes' git push -u origin master
```

If the remote has existing history, fetch and review it before pushing. Do not
force-push over another submission. The AUR remote is
`ssh://aur@aur.archlinux.org/focaltech-fte4800-geekom.git`.

Other maintainers can create an equivalent submission checkout from these
three packaging files. AUR accepts the `master` branch. It does not need the
full driver source or a compiled package in its Git repository.

After a successful submission, users can install with:

```sh
paru -S focaltech-fte4800-geekom
```

## Updates

Update the fixed source commit and hashes when driver source changes. Keep the
DKMS version consistent with `dkms.conf`. Increment `pkgrel` for packaging
changes, regenerate `.SRCINFO`, build and check the package, then commit both
metadata files before pushing:

```sh
makepkg --printsrcinfo > .SRCINFO
```

Do not upload the compiled `.pkg.tar.zst`, vendor DLL, Microsoft archive,
fingerprint data, or local build and device logs to AUR or this GitHub repo.
