"""Reject generated local state in a source distribution."""

from __future__ import annotations

import sys
import tarfile
from pathlib import Path, PurePosixPath

FORBIDDEN_ROOTS = (
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".wrangler",
    "build",
    "dist",
    "site",
)
FORBIDDEN_FILES = (".coverage", ".DS_Store")


def _relative_member(name: str) -> PurePosixPath | None:
    parts = tuple(part for part in PurePosixPath(name).parts if part not in ("", "."))
    if len(parts) < 2:
        return None
    return PurePosixPath(*parts[1:])


def _is_forbidden(name: str) -> bool:
    relative = _relative_member(name)
    if relative is None:
        return False
    if str(relative) in FORBIDDEN_FILES:
        return True
    return any(relative == root or relative.is_relative_to(root) for root in FORBIDDEN_ROOTS)


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write(f"usage: {Path(sys.argv[0]).name} SDIST.tar.gz\n")
        return 2

    archive = Path(sys.argv[1])
    with tarfile.open(archive, "r:*") as source:
        members = source.getnames()
    forbidden = sorted(name for name in members if _is_forbidden(name))
    if forbidden:
        sys.stderr.write(f"{archive}: generated local state found in source distribution:\n")
        for name in forbidden:
            sys.stderr.write(f"  {name}\n")
        return 1

    sys.stdout.write(f"{archive}: {len(members)} entries checked; no generated local state\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
