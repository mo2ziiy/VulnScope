"""Generate local-development secrets for the Docker Compose stack (Task 01.1b).

Writes random values into `infra/.secrets/` (git-ignored). Values are never printed.
Existing files are kept unless `--force` is given, so a running database keeps working.

Local development only: these are not production credentials.
"""

import argparse
import os
import secrets
import sys
from pathlib import Path

SECRETS_DIR = Path(__file__).resolve().parent.parent / "infra" / ".secrets"
SECRET_FILES = ["postgres_password"]


def write_secret(path: Path) -> None:
    value = secrets.token_urlsafe(32)  # 256 bits from the OS CSPRNG
    tmp = path.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="") as f:
        f.write(value)
    os.replace(tmp, path)
    path.chmod(0o600)  # effective on POSIX; Windows ignores most mode bits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="overwrite existing secrets")
    args = parser.parse_args()

    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    for name in SECRET_FILES:
        path = SECRETS_DIR / name
        if path.exists() and not args.force:
            print(f"kept existing {path.relative_to(SECRETS_DIR.parent.parent)}")
            continue
        write_secret(path)
        print(f"wrote {path.relative_to(SECRETS_DIR.parent.parent)} (value not shown)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
