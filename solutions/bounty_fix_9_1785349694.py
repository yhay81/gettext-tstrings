### Technical Overview

The Babel extraction guide documents support for both `babel.cfg` (INI format) and `babel.toml` (TOML format) configuration files. While unit tests exist for TOML configuration parsing in `babel.messages.extract`, end-to-end testing via the `pybabel` command-line interface frontend previously only tested `babel.cfg`.

To ensure that end-to-end integration remains intact—including CLI argument handling, entry point discovery, TOML option processing (e.g., list-valued options such as `keywords`), and output generation—this fix adds an end-to-end test for `babel.toml` extraction in `tests/messages/test_frontend.py`.

#### Key Highlights of the Test Case:
1. **TOML Support Guard**: Checks for `tomllib` (standard library in Python 3.11+) or `tomli` backport, gracefully skipping the test if neither module is available.
2. **Configuration Setup**: Creates a temporary project directory containing source code with standard and custom translation function calls (`_` and `custom_gettext`).
3. **TOML Format Validation**: Writes a `babel.toml` file utilizing the `[[mapping]]` array of tables format and TOML list values for `keywords` (`["_", "custom_gettext"]`).
4. **End-to-End Extraction**: Invokes `CommandLineInterface().run(...)` with `pybabel extract -F babel.toml` to extract messages into a `.pot` catalog file.
5. **Assertions**: Validates that the output file exists and contains all expected extracted strings.

---

### Solution Code

Add the following test case to `tests/messages/test_frontend.py`:

```python
import sys
import pytest
from babel.messages import frontend

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@pytest.mark.skipif(tomllib is None, reason="tomllib or tomli is required for TOML support")
def test_extract_with_babel_toml(tmp_path):
    """End-to-end test for pybabel extract using a babel.toml mapping file."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Create source file with translatable messages
    py_file = project_dir / "app.py"
    py_file.write_text(
        'print(_("Hello from babel.toml!"))\n'
        'print(custom_gettext("Custom keyword string"))\n',
        encoding="utf-8",
    )

    # Create babel.toml mapping file with TOML list values for keywords
    toml_file = project_dir / "babel.toml"
    toml_file.write_text(
        '[extractors]\n\n'
        '[[mapping]]\n'
        'method = "python"\n'
        'pattern = "**.py"\n'
        'encoding = "utf-8"\n'
        'keywords = ["_", "custom_gettext"]\n',
        encoding="utf-8",
    )

    output_file = project_dir / "messages.pot"

    # Run pybabel extract end-to-end via CLI interface
    cli = frontend.CommandLineInterface()
    cli.run([
        'pybabel',
        'extract',
        '-F', str(toml_file),
        '-o', str(output_file),
        str(project_dir),
    ])

    # Assert POT catalog file was generated and contains expected extracted strings
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Hello from babel.toml!" in content
    assert "Custom keyword string" in content
```