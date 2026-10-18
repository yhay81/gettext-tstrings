# /// script
# # Weblate supports 3.12 and newer; pinning the oldest keeps this environment
# # from moving with whichever interpreter uv finds newest.
# requires-python = "==3.12.*"
# dependencies = [
#   "psycopg[binary]==3.3.6",
#   "weblate==2026.10.1",
# ]
#
# [tool.uv]
# # Only Weblate's backup feature needs borgbackup, which has no wheel for every
# # platform and would have to be compiled.
# exclude-dependencies = ["borgbackup"]
# ///
"""The Weblate half of the round trip: import, translate, check, export.

run.py calls this as ``uv run --script weblate_side.py INPUT OUTPUT``. INPUT
holds ``messages.pot`` and ``locale/pl/LC_MESSAGES/messages.po``; OUTPUT
receives what Weblate exported and ``results.json``, which records the
versions, the component settings, and what every check said about every
translation entered.

A throwaway PostgreSQL cluster runs for the length of the call, from the server
binaries in $PG_BIN or the first installation found, on 127.0.0.1 with a random
password, and is stopped however the run ends. Weblate runs with Celery tasks
executed in place, so no Redis or worker is needed.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from collections.abc import Generator
from contextlib import contextmanager
from importlib.metadata import version
from pathlib import Path
from typing import Any

LANGUAGE = "pl"
# (context, source) of the unit, then the forms entered. The broken ones go in
# first and stay until the valid ones replace them, so that the catalog Weblate
# exports between the two is what a translator who ignored the checks would ship.
BROKEN = [
    ("renamed placeholder", ("", "Welcome back, {name}"), ["Witaj ponownie, {imie}"]),
    ("conversion added", ("", "Hello {name}"), ["Cześć, {name!r}"]),
    (
        "second plural form drops {n}",
        ("", "{n} file"),
        ["{n} plik", "pliki", "{n} plików"],
    ),
    (
        "first plural form drops {n}",
        ("", "{n} file"),
        ["plik", "{n} pliki", "{n} plików"],
    ),
]
VALID = [
    ("singular", ("", "Welcome back, {name}"), ["Witaj ponownie, {name}"]),
    ("plural", ("", "{n} file"), ["{n} plik", "{n} pliki", "{n} plików"]),
    ("context: button", ("button", "Open"), ["Otwórz"]),
    ("context: state", ("state", "Open"), ["Otwarte"]),
    (
        "reordered",
        ("", "Moved {item} to {folder}"),
        ["Do folderu {folder} przeniesiono {item}"],
    ),
    (
        "repeated in the source",
        ("", "{player} beat {opponent}, and {player} moves on"),
        ["{player} pokonuje gracza {opponent} i {player} przechodzi dalej"],
    ),
    (
        "repeated in the translation",
        ("", "Hello {name}"),
        ["Cześć, {name}! Miło cię znowu widzieć, {name}"],
    ),
]


def find_postgres() -> Path:
    candidates = [os.environ["PG_BIN"]] if os.environ.get("PG_BIN") else []
    for pattern in ("/opt/homebrew/opt/postgresql@*/bin", "/usr/local/opt/postgresql@*/bin"):
        candidates += sorted((str(p) for p in Path("/").glob(pattern[1:])), reverse=True)
    candidates += sorted((str(p) for p in Path("/usr/lib/postgresql").glob("*/bin")), reverse=True)
    if server := shutil.which("postgres"):
        candidates.append(str(Path(server).parent))
    for candidate in candidates:
        if all((Path(candidate) / tool).is_file() for tool in ("postgres", "initdb", "pg_ctl")):
            return Path(candidate)
    msg = "no PostgreSQL server binaries found; set PG_BIN to the directory holding initdb"
    raise SystemExit(msg)


@contextmanager
def postgres(work: Path) -> Generator[dict[str, str]]:
    """A cluster of one database, reachable only from 127.0.0.1, for this run."""
    binaries = find_postgres()
    # macOS: without a valid locale the postmaster turns multithreaded during
    # startup and refuses to run.
    env = {**os.environ, "LC_ALL": "C"}
    data, password = work / "pgdata", secrets.token_hex(16)
    (work / "pwfile").write_text(password + "\n", encoding="utf-8")
    subprocess.run(
        [binaries / "initdb", "-D", data, "-U", "postgres", "--auth=scram-sha-256",
         f"--pwfile={work / 'pwfile'}", "--encoding=UTF8", "--no-locale"],
        check=True, capture_output=True, env=env,
    )  # fmt: skip
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = str(probe.getsockname()[1])
    # No Unix socket: its path would be too long for macOS under a temp dir.
    options = f"-p {port} -c listen_addresses=127.0.0.1 -k ''"
    log = work / "postgres.log"
    subprocess.run(
        [binaries / "pg_ctl", "-D", data, "-l", log, "-w", "-o", options, "start"],
        check=True, capture_output=True, env=env,
    )  # fmt: skip
    try:
        server = subprocess.run(
            [binaries / "postgres", "--version"], check=True, capture_output=True, text=True
        ).stdout.strip()
        subprocess.run(
            [binaries / "psql", "-h", "127.0.0.1", "-p", port, "-U", "postgres", "-c",
             "CREATE DATABASE weblate"],
            check=True, capture_output=True, env={**env, "PGPASSWORD": password},
        )  # fmt: skip
        yield {"port": port, "password": password, "version": server}
    finally:
        subprocess.run(
            [binaries / "pg_ctl", "-D", data, "-m", "fast", "-w", "stop"],
            check=False, capture_output=True, env=env,
        )  # fmt: skip


SETTINGS = """
from weblate.settings_example import *  # noqa: F403

DEBUG = False
SECRET_KEY = {secret!r}
SITE_DOMAIN = "weblate.invalid"
DATA_DIR = {data!r}
CACHE_DIR = DATA_DIR + "/cache"
MEDIA_ROOT = DATA_DIR + "/media"
STATIC_ROOT = DATA_DIR + "/static"
DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "127.0.0.1",
        "PORT": {port!r},
        "NAME": "weblate",
        "USER": "postgres",
        "PASSWORD": {password!r},
    }}
}}
CACHES = {{
    "default": {{"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    "avatar": {{"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
}}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "memory://localhost/"
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_RESULT_BACKEND = None
CREATE_GLOSSARIES = False
LOGGING = {{
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {{"console": {{"class": "logging.StreamHandler"}}}},
    "root": {{"handlers": ["console"], "level": "WARNING"}},
}}
"""


def checks_of(unit: Any) -> list[dict[str, str]]:
    found = []
    for check in unit.all_checks:
        description = str(check.get_description())
        # The description is HTML for the editor; keep its text.
        text = re.sub(r"<[^>]+>", "", description.replace("<br />", "; "))
        found.append({"check": check.name, "says": text})
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with (
        tempfile.TemporaryDirectory(prefix="weblate-experiment-") as tmp,
        postgres(Path(tmp)) as db,
    ):
        work = Path(tmp)
        settings = SETTINGS.format(
            secret=secrets.token_hex(32),
            data=str(work / "data"),
            **{k: db[k] for k in ("port", "password")},
        )
        (work / "experiment_settings.py").write_text(textwrap.dedent(settings), encoding="utf-8")
        sys.path.insert(0, str(work))
        os.environ["DJANGO_SETTINGS_MODULE"] = "experiment_settings"

        import django

        django.setup()
        from django.core.management import call_command
        from weblate.auth.models import User
        from weblate.lang.models import Language
        from weblate.trans.models import Component, Project
        from weblate.utils.state import STATE_TRANSLATED
        from weblate.utils.views import create_component_from_zip

        call_command("migrate", interactive=False, verbosity=0)

        # The same path Weblate's own "upload translation files" form and its
        # REST API take: a ZIP becomes a component with no remote repository.
        project = Project.objects.create(
            name="Experiment", slug="experiment", web="https://weblate.invalid/"
        )
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as zf:
            zf.write(args.input / "messages.pot", "locale/messages.pot")
            path = f"locale/{LANGUAGE}/LC_MESSAGES/messages.po"
            zf.write(args.input / path, path)
        archive.seek(0)
        params = {
            "name": "Messages",
            "slug": "messages",
            "project": project,
            "vcs": "local",
            "repo": "local:",
            "branch": "main",
            "file_format": "po",
            "filemask": "locale/*/LC_MESSAGES/messages.po",
            "new_base": "locale/messages.pot",
            "template": "",
            "source_language": Language.objects.get(code="en"),
        }
        create_component_from_zip(params, archive)
        component = Component.objects.create(**params)
        translation = component.translation_set.get(language__code=LANGUAGE)
        user = User.objects.create(
            username="experiment", full_name="Experiment", email="experiment@weblate.invalid"
        )
        units = {(u.context, u.get_source_plurals()[0]): u.pk for u in translation.unit_set.all()}
        Unit = type(translation.unit_set.first())  # noqa: N806

        imported = [
            {
                "context": unit.context,
                "source": unit.get_source_plurals(),
                "flags": unit.all_flags.format(),
            }
            for unit in translation.unit_set.order_by("position")
        ]

        def enter(label: str, key: tuple[str, str], forms: list[str]) -> dict[str, object]:
            unit = Unit.objects.get(pk=units[key])
            unit.translate(user, forms, STATE_TRANSLATED)
            unit = Unit.objects.get(pk=units[key])
            return {"case": label, "context": key[0], "source": key[1], "entered": forms,
                    "checks": checks_of(unit)}  # fmt: skip

        broken = [enter(*case) for case in BROKEN]
        translation.commit_pending("experiment: broken translations", user)
        shutil.copyfile(translation.get_filename(), args.output / f"{LANGUAGE}.unchecked.po")
        valid = [enter(*case) for case in VALID]
        translation.commit_pending("experiment: valid translations", user)
        shutil.copyfile(translation.get_filename(), args.output / f"{LANGUAGE}.po")

        results = {
            "versions": {
                "python": sys.version.split()[0],
                **{name: version(name) for name in ("weblate", "django", "translate-toolkit")},
                "postgresql": db["version"],
            },
            "component": {
                "file_format": component.file_format,
                "vcs": component.vcs,
                "filemask": component.filemask,
                "new_base": component.new_base,
                "source_language": component.source_language.code,
                "check_flags": component.check_flags,
                "enforced_checks": list(component.enforced_checks),
                "language": LANGUAGE,
                "plural_formula": translation.plural.formula,
                "plural_forms": translation.plural.number,
            },
            "imported": imported,
            "broken": broken,
            "valid": valid,
        }
    (args.output / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
