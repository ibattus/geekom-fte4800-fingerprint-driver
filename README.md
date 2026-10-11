# GEEKOM FTE4800 / FT9368 fingerprint driver

Arch Linux fingerprint support for the **GEEKOM NX14CM**, using the FocalTech
FTE4800 SPI reader with an FT9368 sensor. This is a downstream adaptation of
[Bharath Yadav's FTE4800 Linux driver](https://github.com/1bharath-yadav/focaltech-fte4800-linux-driver).

## Tested status

On one GEEKOM NX14CM running Arch Linux and KDE Plasma:

- Reader initialization and real fingerprint capture succeeded.
- Enrollment and a separate `fprintd-verify` returned `verify-match`.
- KDE's user settings can enroll additional fingers.
- A graphical administrator prompt authenticated with a fingerprint; the user
  confirmed that the dialog disappeared after touching the reader.
- The 44 inherited source tests and three libfprint core unit suites passed.

The installed and tested package is `focaltech-fte4800 1.0.3-5`.
Login and lock-screen PAM rules are supplied, but their successful live
operation, a subsequent reboot, and suspend/resume have not been confirmed.
The driver is not claimed to support every machine with the FTE4800 ACPI ID.

## Changes for this machine

- Select SPI mode 0 with **active-high chip select** (`SPI_CS_HIGH`, numeric
  mode 4), 1 MHz. The board's ACPI chip-select polarity is misleading.
- Use `memmove` for an overlapping SPI request buffer.
- Disable the IRQ without synchronously waiting for a worker that needs the
  mutex already held by the ioctl handler.
- Complete verification when the matcher returns, rather than waiting for
  finger release and risking a PAM timeout.
- Report low-quality captures as retry results instead of fatal failures.
- Use `auth substack` for password fallback. A fingerprint success skips the
  entire password stack; using `include` would skip only its first module.

Hardware reports FT9368, firmware date 2022-07-29, and a 64 × 80 pixel frame.
Reset is HIGH → LOW for 10 ms → HIGH, followed by a 350 ms boot wait.
The implementation details are in `protocol/`, `focal_spi.c`, and
`libfprint/drivers/`.

## How it works

`focal_spi` DKMS transport → private libfprint → stock Arch `fprintd` → PAM.

Fingerprint matching uses FocalTech's native WinBio engine through the
upstream project's PE/WinBio bridge. The package fetches the proprietary
engine from Microsoft Update Catalog and verifies both the archive and DLL
hashes. No vendor DLL, fingerprint template, capture, or local device log is
included in this repository. The distro's libfprint is left in place;
a systemd drop-in selects the private library for `fprintd`.

## Build and install on Arch

Run from this repository's root. Install headers matching your kernel;
`linux-headers` below is for the standard Arch `linux` kernel. LTS and other
kernels need their corresponding headers.

```sh
sudo pacman -Syu --needed base-devel git dkms linux-headers
cd packaging/arch
makepkg --cleanbuild --syncdeps
sudo systemctl stop fprintd
sudo pacman -U ./focaltech-fte4800-1.0.3-5-x86_64.pkg.tar.zst
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
sudo modprobe focal_spi
sudo systemctl start fprintd
```

If another `focal_spi` module was already loaded, unload it with
`sudo modprobe -r focal_spi` after stopping `fprintd`, before loading the new
one. Close fingerprint enrollment and verification tools first.
A live module reload was sufficient on the tested machine; it was not rebooted.

The package replaces `focaltech-spi-dkms` and provides its dependency name.
Check `dkms status` if installation reports missing kernel headers or a build
failure. The installed module has an FTE4800 ACPI alias for discovery at boot.

## AUR package preparation

A self-contained `focaltech-fte4800-geekom` recipe is available in
[packaging/aur/](packaging/aur/README.md), including generated `.SRCINFO`.
It downloads pinned source archives and has passed a standalone package build
and the three libfprint core unit suites. **It has not yet been submitted to
AUR**; an AUR account with a registered SSH key is still needed.

## Enroll and verify

```sh
fprintd-list "$USER"
fprintd-enroll -f right-index-finger "$USER"
fprintd-verify -f right-index-finger "$USER"
```

Touch and lift as enrollment requests. On KDE Plasma, additional fingers can
also be added in **System Settings → Users → Configure Fingerprint Authentication**.

## Password prompts, login, and locking

Enrollment alone does not enable fingerprint authentication for every service.
See [the reviewed Arch/KDE PAM examples](install/pam/README.md). They retain
password fallback and account checks. Installation of the driver package does
not automatically change PAM policy.

The examples scan first for `sudo`, graphical administrator prompts, and SDDM.
KDE Plasma already supplies a separate `kde-fingerprint` PAM service on the
tested installation. KWallet may still need its password after fingerprint
login, because the fingerprint does not provide the wallet's decryption key.

## Development and validation

```sh
tests/run-tests.sh
for script in install/*.sh tests/run-tests.sh tools/*.sh packaging/arch/PKGBUILD; do
  bash -n "$script" || exit
done
git diff --check
```

After building the package:

```sh
meson test -C packaging/arch/src/libfprint/build --suite unit-tests --print-errorlogs
```

Diagnostics include `tools/geekom_identity_probe.py` and
`tools/fte4800_selftest.py`. Stop `fprintd` before accessing the sensor directly
with a root diagnostic tool. They interact with the actual reader.

The separate upstream AppStream metadata test had metadata warnings, including
an unreachable issue URL. Driver/emulation tests requiring unavailable hardware
were skipped in the original build. No false-accept/false-reject rates or
security certification have been established; see [SECURITY.md](SECURITY.md).

## Removal

Restore any PAM files you changed from your backups first, then:

```sh
sudo systemctl stop fprintd
sudo modprobe -r focal_spi
sudo pacman -Rns focaltech-fte4800
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

Fingerprint enrollment data is managed by `fprintd`, separately from the
package. This procedure does not delete your saved enrollments.

## Credits and licenses

The original project and native vendor-engine bridge are by Bharath Yadav.
This adaptation derives from upstream commit
`fda69b646236bea9d2a798bca99e1c8b960e9c14`. It starts with a clean Git history
because older upstream commits included proprietary binaries and fingerprint
captures. The original README is preserved
in [docs/UPSTREAM-README.md](docs/UPSTREAM-README.md).

Kernel source is GPL-2.0-only; libfprint integration is LGPL-2.1-or-later.
See [LICENSES/](LICENSES/). The proprietary FocalTech DLL has separate terms;
this project does not claim redistribution rights for it.

See [PUBLISHING.md](PUBLISHING.md) for publishing this prepared repository.
