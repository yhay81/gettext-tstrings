"""The messages the Weblate round trip carries: one of each shape a catalog has.

run.py extracts this file with the package's Babel extractor, as ``pybabel
extract`` does for an application, and after the round trip renders these same
calls against the catalog Weblate exported.
"""

from __future__ import annotations

from gettext_tstrings import ntr, pgettext, tr


def messages(
    name: str, n: int, item: str, folder: str, player: str, opponent: str
) -> dict[str, str]:
    return {
        # Translators: shown on the dashboard right after sign-in
        "singular": tr(t"Welcome back, {name}"),
        "plural": ntr(t"{n} file", t"{n} files", n),
        "context: button": pgettext("button", t"Open"),
        "context: state": pgettext("state", t"Open"),
        "reordered": tr(t"Moved {item} to {folder}"),
        "repeated in the source": tr(t"{player} beat {opponent}, and {player} moves on"),
        "repeated in the translation": tr(t"Hello {name}"),
    }
