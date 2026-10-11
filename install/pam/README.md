# Arch Linux / KDE PAM examples

These files are references derived from the working Arch configuration, not
an automatic installer. Compare them with your installed files and retain your
existing account, session, password, and desktop keyring settings.

Back up each file before editing, keep an authenticated administrator terminal
open, and verify password fallback before closing it. For a service that exists
only in `/usr/lib/pam.d`, create a reviewed override in `/etc/pam.d` rather than
editing the package-owned file.

| Example | Service file | Verified here |
| --- | --- | --- |
| `sudo.example` | `/etc/pam.d/sudo` | Rules reviewed; live success not confirmed |
| `polkit-1.example` | `/etc/pam.d/polkit-1` | Graphical administrator fingerprint authentication |
| `sddm.example` | `/etc/pam.d/sddm` | Rules reviewed; live success not confirmed |

Replace the service's original `auth include system-auth` line (or
`auth include system-login` for SDDM) with the corresponding marked block.
Do not duplicate the original authentication include after the block.
The account and session includes stay in place. SDDM's optional keyring
modules also stay in place.

The central rule is:

```pam
auth [success=1 default=ignore] pam_fprintd.so max-tries=3 timeout=15
auth substack system-auth
```

A successful fingerprint jumps over **one complete substack**. `include` does
not count as one module: it expands the referenced file inline. Using it here
caused a successful fingerprint scan to continue into password authentication.
SDDM uses `system-login` as the substack instead of `system-auth`.

The outer `pam_faillock.so preauth` checks existing account lockouts before the
scan, and `authsucc` clears the failure history after successful authentication.
Password fallback still runs the normal Arch authentication stack.
`sudo` uses a 10-second scan timeout and skips fingerprint scanning for a
noninteractive invocation without a terminal. The graphical services use 15
seconds. A failed scan proceeds to the normal password prompt.

On the tested KDE installation, `/usr/lib/pam.d/kde-fingerprint` already uses
`pam_fprintd.so`, and no lock-screen PAM edit was needed. Check your local
file; do not assume every desktop distribution supplies it.

These are persistent file settings. Actual post-reboot login and lock-screen
fingerprint success have not been validated on this machine.

To undo the changes, restore your original service files. If `polkit-1` had no
original `/etc/pam.d` override, remove the new override to use the packaged file.
