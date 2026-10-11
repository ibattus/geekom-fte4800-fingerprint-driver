# Validation record — 2026-10-11

Target: GEEKOM NX14CM, FocalTech ACPI FTE4800 SPI device, FT9368 chip,
firmware 2022-07-29, 64 × 80 grayscale pixels. Environment: Arch Linux,
Linux 7.2.9-arch1-1, KDE Plasma 6.7.5, SDDM 0.21.0.

| Check | Result |
| --- | --- |
| Repeatable identity / geometry | Passed, SPI numeric mode 4 at 1 MHz |
| Arch package build | Passed, `focaltech-fte4800 1.0.3-5` |
| DKMS installation and live module reload | Passed |
| fprintd claim and native matching-engine initialization | Passed |
| Live enrollment | Passed |
| Separate fprintd verification | `verify-match (done)` |
| Graphical administrator authentication | Passed after PAM correction; user confirmed |
| Inherited repository source tests | 44 passed, rerun in this prepared checkout |
| libfprint core unit suites | Three suites passed on the installed build's source tree |
| Shell syntax / staged whitespace | Passed in this prepared checkout |
| Fresh source files versus installed build's sources | Identical |
| Login and KDE lock-screen live success | Unconfirmed; background login tests timed out without another capture |
| Later boot and suspend/resume | Not tested |

The broader libfprint test run had an AppStream metadata failure, including
an unreachable issue URL; 29 unavailable driver/emulation tests were skipped.

No restart of the computer was performed. Service and kernel module reloads
were sufficient for the installed driver. Physical enrollment and verification
logs are kept outside this publication checkout because they contain local
user and device information.

PAM debugging identified two separate problems: waiting for finger release
could consume the authentication timeout, and an `include` after a `success=1`
jump expanded inline instead of skipping the complete password stack. The
source now reports matches immediately, and the examples use `substack`.
