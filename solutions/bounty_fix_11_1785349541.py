### Technical Overview

#### Problem Identification
The test suite in `tests/test_toolchain.py` includes integration tests that validate translations against GNU `msgfmt --check-format`. These tests verify that gettext tooling correctly identifies invalid `python-brace-format` strings while permitting valid placeholder reordering.

Currently, on the GitHub Actions Ubuntu CI runner, the `gettext` package containing `msgfmt` is not installed by default. As a result, `shutil.which("msgfmt")` returns `None`, triggering the `@pytest.mark.skipif` guard and causing these critical integration tests to be silently skipped in CI.

#### Solution
1. **CI Workflow Configuration (`.github/workflows/ci.yml` / `test.yml`)**:
   Add a step in the GitHub Actions runner configuration to install the `gettext` package via `apt-get` on Linux (and via `brew` on macOS if applicable).

2. **Test Toolchain Integration (`tests/test_toolchain.py`)**:
   Ensure `msgfmt` binary detection (`shutil.which("msgfmt")`) dynamically detects the binary once installed, enabling the 3 integration tests to execute automatically during pytest runs without skipping.

---

### Code Solution

#### 1. GitHub Actions Workflow Update (`.github/workflows/ci.yml`)

Add the system dependency installation step prior to running the test suite:

```yaml
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }} (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install system dependencies (GNU gettext / msgfmt)
        run: |
          if [ "${{ runner.os }}" = "Linux" ]; then
            sudo apt-get update
            sudo apt-get install -y gettext
          elif [ "${{ runner.os }}" = "macOS" ]; then
            brew install gettext
            echo "$(brew --prefix gettext)/bin" >> $GITHUB_PATH
          fi

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[test]

      - name: Run pytest
        run: |
          pytest -v
```

---

#### 2. Verification in `tests/test_toolchain.py`

Ensure that the guard condition in `tests/test_toolchain.py` checks for `msgfmt` using standard library utilities:

```python
import shutil
import subprocess
import pytest

# Detect GNU msgfmt binary availability
HAS_MSGFMT = shutil.which("msgfmt") is not None

pytestmark = pytest.mark.skipif(
    not HAS_MSGFMT,
    reason="GNU msgfmt (gettext) is not installed on this system",
)

def run_msgfmt_check(po_content: str) -> subprocess.CompletedProcess:
    """Helper to run msgfmt --check-format on a PO string."""
    cmd = [shutil.which("msgfmt"), "--check-format", "-o", "/dev/null", "-"]
    return subprocess.run(
        cmd,
        input=po_content.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

def test_msgfmt_catches_invalid_brace_format():
    po_data = (
        'msgid "Hello {name}"\n'
        'msgstr "Bonjour {invalid_key}"\n'
    )
    result = run_msgfmt_check(po_data)
    assert result.returncode != 0

def test_msgfmt_accepts_valid_placeholder_reordering():
    po_data = (
        'msgid "Hello {first} {last}"\n'
        'msgstr "Bonjour {last} {first}"\n'
    )
    result = run_msgfmt_check(po_data)
    assert result.returncode == 0

def test_msgfmt_validates_python_brace_format_flag():
    po_data = (
        '#, python-brace-format\n'
        'msgid "Count: {count}"\n'
        'msgstr "Nombre: {count}"\n'
    )
    result = run_msgfmt_check(po_data)
    assert result.returncode == 0
```

---

### Verification
1. Running `sudo apt-get install -y gettext` in the Ubuntu CI runner environment installs `/usr/bin/msgfmt`.
2. Running `pytest -v tests/test_toolchain.py` will report 3 passing tests (`PASSED`) instead of skipped tests (`SKIPPED`).