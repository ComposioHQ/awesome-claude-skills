---
name: arch-pkgbuild-review
description: Review and fix Arch Linux PKGBUILDs before submitting to a repository (BlackArch/AUR), covering template choice, venv handling, install hooks, and pkgcheck. Use when writing, reviewing, or debugging a PKGBUILD or .install file.
---

# Arch PKGBUILD Review

Review and correct an Arch Linux package build before it is submitted to a
repository such as BlackArch or the AUR. The focus is the failure modes that
actually break builds or get a submission rejected.

## When to Use This Skill

- Before opening a package submission PR (BlackArch, AUR, personal repo).
- When `makepkg` fails and the error is not obvious from the message.
- When a package builds but the resulting tool does not run.
- When a maintainer asks for changes on an existing PKGBUILD.

## What This Skill Does

1. **Template choice**: picks the right base template instead of improvising.
   - Python tool with volatile deps (boto3, typer, pydantic, mcp, ...) →
     `python-standalone` (isolated venv, built at install time).
   - Python tool whose deps exist in the official repos → `python-community`.
   - Rust/Go/Node tool → the corresponding language template.
2. **Venv placement**: the venv must be created in `post_install()` in the
   `.install` file, never in `package()` inside the PKGBUILD. A venv built in
   `package()` ends up inside the package archive and breaks bsdtar or ships
   stale absolute paths.
3. **Install hooks**: verifies `post_install()` exists, that `post_upgrade()`
   updates in place with `-U` instead of recreating the venv, and that
   `post_remove()` cleans the untracked venv directory.
4. **Launcher correctness**: the wrapper in `/usr/bin` must invoke the real
   entry point by absolute path (for example
   `exec python /usr/share/<name>/<entry>.py "$@"`), not rely on a console
   script shim that only exists if the upstream project defines one.
5. **Runtime files**: checks that everything the tool reads at runtime is
   shipped (README.md when the pyproject declares `readme=`, data/template
   directories, `requirements.txt` when `post_install()` reads it).
6. **pkgcheck**: runs `pkgcheck` and requires a clean result, including the
   trailing newline at the end of the PKGBUILD (error E060 otherwise).

## How to Use

### Basic Usage

```
Review this PKGBUILD before I submit it.
```

### Advanced Usage

```
This makepkg build fails with <error> on Arch / Python 3.14. Find the cause
and the smallest fix that keeps it within the python-standalone template.
```

## Example

**User**: "My Python tool builds but the command does nothing when installed."

**Output**:

```
The launcher runs `python /usr/share/<name>/<entry>.py`, but the package does
not ship `requirements.txt`, so `post_install()` fails and the venv is never
populated. Ship requirements.txt (or the pyproject) in the share directory, or
point the venv build at the file that is actually installed.
```

**Inspired by:** packaging work on BlackArch (packages cloud-audit, dragonrepo,
rusthound, lol), where each of these failure modes appeared in a real build.

## Tips

- Build with `makepkg -f` on the host first, then confirm what actually landed
  in the archive with `tar -tf <pkg>.pkg.tar.zst`.
- A venv should never appear in the archive: `tar -tf ... | grep -c 'venv/'`
  must print `0`.
- Rust crates pinned years ago often fail on current rustc; bump only the
  offending crate (`cargo update -p <crate> --precise <ver>`) instead of
  regenerating the whole lockfile.
- Missing system libraries surface as build-script failures (for example
  bindgen needing libclang): add the package to `makedepends` rather than
  installing it by hand.
- Reproduce `post_install()` in a scratch prefix and run the launcher before
  submitting; a package that builds can still be unusable.

## Common Use Cases

- Preparing a new tool submission for BlackArch.
- Fixing a PKGBUILD that a maintainer rejected.
- Diagnosing a `makepkg` failure on a current Arch toolchain.
- Checking that a packaged CLI actually runs after install.
