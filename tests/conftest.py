from __future__ import annotations

import gettext
import io
from pathlib import Path

import pytest
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_translations() -> object:
    def load(locale: str) -> gettext.GNUTranslations:
        po_path = FIXTURES / "locales" / locale / "LC_MESSAGES" / "messages.po"
        with po_path.open("rb") as po_file:
            catalog = read_po(po_file, locale=locale)
        mo_file = io.BytesIO()
        write_mo(mo_file, catalog)
        mo_file.seek(0)
        return gettext.GNUTranslations(mo_file)

    return load
