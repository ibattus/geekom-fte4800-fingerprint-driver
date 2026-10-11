# Publish the prepared repository

This repository is published at
https://github.com/ibattus/geekom-fte4800-fingerprint-driver.
The original project is retained as the `upstream` remote.
The commands below describe how to publish your own copy.

Review locally:

```sh
git status
git log -2 --oneline
git remote -v
```

Create and push a new public GitHub repository with GitHub CLI:

```sh
gh auth login
gh repo create geekom-fte4800-fingerprint-driver --public --source=. --remote=origin --push
```

Or create an empty repository on GitHub, without initializing a README, then:

```sh
git remote add origin https://github.com/YOUR_USERNAME/geekom-fte4800-fingerprint-driver.git
git push -u origin main
```

Use `--private` instead of `--public` if you want a private repository.
Git author details use the machine's existing Git configuration. You can inspect
and change the repository-local identity before publishing if desired.

For updates to this repository, commit your reviewed changes and run
`git push origin main`.

Do not add package archives, vendor binaries, fingerprint data, local logs,
credentials, or personal system configuration backups. `.gitignore` excludes
these artifacts. Documentation distinguishes confirmed administrator prompt
success from unconfirmed live login, lock-screen, and reboot behavior.
