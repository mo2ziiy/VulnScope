"""Run detect-secrets against every tracked or untracked-but-not-ignored file (SAC-SEC-01).

Exits non-zero when a potential secret is found that isn't recorded in `.secrets.baseline`.

Two passes:
1. All files except lockfiles and the baseline: every detector, compared to the baseline.
2. Lockfiles: structured detectors only (keys, tokens, private keys). The entropy detectors
   are disabled there because integrity hashes look like high-entropy strings. detect-secrets
   also treats the `.lock` extension as non-text and would silently skip `uv.lock`, so that
   filter is disabled for this pass only (both lockfiles are plain text).

File names are read NUL-separated (`git ls-files -z`) so names with spaces, non-ASCII or
other unusual characters reach the scanner unchanged instead of in git's quoted form.
"""

import os
import subprocess
import sys

LOCKFILES = {"pnpm-lock.yaml", "uv.lock"}
BASELINE = ".secrets.baseline"
ENTROPY_PLUGINS = ["Base64HighEntropyString", "HexHighEntropyString"]
NON_TEXT_FILTER = "detect_secrets.filters.heuristic.is_non_text_file"

# Fixed argument lists, no shell. Executables are resolved from PATH on purpose:
# `git` from the developer's install, `detect-secrets-hook` from the uv-managed venv.
LIST_FILES = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
HOOK = ["detect-secrets-hook"]


def repo_files() -> list[str]:
    listed = subprocess.run(LIST_FILES, check=True, capture_output=True)  # noqa: S603
    names = listed.stdout.decode("utf-8").split("\0")
    # Tracked files deleted from the working tree can't be scanned (and won't be committed).
    return sorted({n for n in names if n and os.path.isfile(n)})


def main() -> int:
    files = repo_files()
    general = [f for f in files if f not in LOCKFILES and f != BASELINE]
    locks = [f for f in files if f in LOCKFILES]
    print(f"detect-secrets: {len(general)} files (all detectors), {len(locks)} lockfiles")

    status = subprocess.call([*HOOK, "--baseline", BASELINE, *general])  # noqa: S603
    if locks:
        disabled = [arg for p in ENTROPY_PLUGINS for arg in ("--disable-plugin", p)]
        disabled += ["--disable-filter", NON_TEXT_FILTER]
        status |= subprocess.call([*HOOK, *disabled, *locks])  # noqa: S603
    return 1 if status else 0


if __name__ == "__main__":
    sys.exit(main())
