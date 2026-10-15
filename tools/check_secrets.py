"""Run detect-secrets against every tracked or untracked-but-not-ignored file (SAC-SEC-01).

Fails (non-zero exit) when a potential secret is found that isn't already recorded in
`.secrets.baseline`. Lockfiles and the baseline itself are skipped: they contain
integrity hashes that look like high-entropy strings but aren't secrets.
"""

import subprocess
import sys

SKIPPED = {"pnpm-lock.yaml", "uv.lock", ".secrets.baseline"}

# Fixed argument lists, no shell. Executables are resolved from PATH on purpose:
# `git` from the developer's install, `detect-secrets-hook` from the uv-managed venv.
LIST_FILES = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]


def main() -> int:
    listed = subprocess.run(LIST_FILES, check=True, capture_output=True, text=True)  # noqa: S603
    files = [f for f in listed.stdout.splitlines() if f and f not in SKIPPED]
    print(f"detect-secrets: scanning {len(files)} files")
    hook = ["detect-secrets-hook", "--baseline", ".secrets.baseline", *files]
    return subprocess.call(hook)  # noqa: S603


if __name__ == "__main__":
    sys.exit(main())
