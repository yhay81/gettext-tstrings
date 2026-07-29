from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
CHECKER = ROOT / "scripts" / "check_sdist.py"


def _check(archive: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(archive)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_sdist_excludes_generated_local_state(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    for filename in (".gitignore", "LICENSE", "README.md", "pyproject.toml"):
        shutil.copy2(ROOT / filename, project / filename)
    shutil.copytree(ROOT / "src", project / "src")

    for relative in (".cache/private.json", ".wrangler/cache/account.json", "site/index.html"):
        sentinel = project / relative
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text("must not ship", encoding="utf-8")

    output = tmp_path / "dist"
    subprocess.run(
        ["uv", "build", "--sdist", "--out-dir", str(output)],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    archives = list(output.glob("*.tar.gz"))

    assert len(archives) == 1
    result = _check(archives[0])
    assert result.returncode == 0, result.stderr


def test_sdist_check_rejects_a_cache_directory(tmp_path: Path) -> None:
    archive = tmp_path / "broken.tar.gz"
    payload = b"local state"
    member = tarfile.TarInfo("example-1.0/.cache/private.json")
    member.size = len(payload)
    with tarfile.open(archive, "w:gz") as target:
        target.addfile(member, io.BytesIO(payload))

    result = _check(archive)

    assert result.returncode == 1
    assert "example-1.0/.cache/private.json" in result.stderr
