"""The ASGI integration that docs/workflow.md recommends, written as an app would.

``app`` binds the request's catalog in an HTTP middleware around ``call_next``,
which is the documented pattern. ``dependency_app`` binds it in a FastAPI
dependency instead, once from ``async def`` and once from plain ``def``, because
that is the other place an application reaches for and the two do not behave
alike. The one concession to the experiment is ``app.state.pause`` and
``app.state.wait``: the points where a real handler would wait on I/O, which
run.py replaces with barriers.
"""

from __future__ import annotations

import asyncio
import gettext
import io
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from fastapi import BackgroundTasks, Depends, FastAPI, Request, Response
from fastapi.responses import StreamingResponse

from gettext_tstrings import get_translations, lazy_gettext, ntr, tr, use_translations

LOCALES = Path(__file__).parent / "locales"
LANGUAGES = ("ja", "fr")

# Defined at import, before any request has a language — the shape of a form
# label or an enum's display name. It has to render in whichever language the
# request that uses it has bound.
WELCOME = lazy_gettext(t"Welcome")


def _load(language: str) -> gettext.GNUTranslations:
    # Compiled in memory, the way the test suite loads its fixtures: the
    # repository ignores *.mo, and nothing has to be built before a run.
    with (LOCALES / language / "LC_MESSAGES" / "messages.po").open("rb") as file:
        catalog = read_po(file, locale=language)
    compiled = io.BytesIO()
    write_mo(compiled, catalog)
    compiled.seek(0)
    return gettext.GNUTranslations(compiled)


CATALOGS = {language: _load(language) for language in LANGUAGES}

Rendered = dict[str, str | None]


def negotiate_language(header: str | None) -> str:
    # Stands in for real Accept-Language parsing, as it does in the docs.
    return header if header in CATALOGS else LANGUAGES[0]


def bound_language() -> str | None:
    """Which catalog this context has bound, read back from the binding itself."""
    current = get_translations()
    return next((code for code, catalog in CATALOGS.items() if catalog is current), None)


def render(name: str, n: int) -> Rendered:
    return {
        "bound": bound_language(),
        "hello": tr(t"Hello {name}"),
        "files": ntr(t"{n} file", t"{n} files", n),
        "label": str(WELCOME),
    }


async def _no_pause() -> None:
    await asyncio.sleep(0)


def _no_wait() -> None:
    return None


app = FastAPI()
app.state.pause = _no_pause
app.state.wait = _no_wait
# What each failing handler had bound just before it raised, and what each
# background task rendered once the response had gone.
app.state.failed_with = []
app.state.background = []


@app.middleware("http")
async def bind_language(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    language = negotiate_language(request.headers.get("accept-language"))
    with use_translations(CATALOGS[language]):
        return await call_next(request)


@app.get("/greet")
async def greet(request: Request, name: str, n: int) -> dict[str, Rendered]:
    before = render(name, n)
    await request.app.state.pause()
    return {"before": before, "after": render(name, n)}


@app.get("/greet-sync")
def greet_sync(request: Request, name: str, n: int) -> Rendered:
    # FastAPI runs a plain def endpoint in a worker thread from a pool that
    # outlives the request, so the binding has to arrive there with each call.
    request.app.state.wait()
    return render(name, n)


@app.get("/stream")
async def stream(name: str, n: int) -> StreamingResponse:
    # The middleware's `with` block has exited by the time this body is
    # produced: call_next returns as soon as the response starts.
    async def body() -> AsyncIterator[bytes]:
        await asyncio.sleep(0)
        rendered = render(name, n)
        yield f"{rendered['bound']}|{rendered['hello']}|{rendered['label']}".encode()

    return StreamingResponse(body(), media_type="text/plain")


@app.get("/background")
async def background(request: Request, name: str, n: int, tasks: BackgroundTasks) -> Rendered:
    # Runs after the response has been sent, so after the middleware's `with`
    # block has exited as well.
    def record() -> None:
        request.app.state.background.append(render(name, n))

    tasks.add_task(record)
    return render(name, n)


@app.get("/fail")
async def fail(request: Request) -> None:
    request.app.state.failed_with.append(bound_language())
    await request.app.state.pause()
    msg = "the handler failed while its language was bound"
    raise RuntimeError(msg)


dependency_app = FastAPI()
dependency_app.state.pause = _no_pause
# What leaving each dependency's `with` block raised, if anything.
dependency_app.state.teardown = []


async def bind_in_async_dependency(request: Request) -> AsyncIterator[None]:
    language = negotiate_language(request.headers.get("accept-language"))
    try:
        with use_translations(CATALOGS[language]):
            yield
    except Exception as exc:
        dependency_app.state.teardown.append(f"async def: {type(exc).__name__}: {exc}")
        raise


def bind_in_sync_dependency(request: Request) -> Iterator[None]:
    language = negotiate_language(request.headers.get("accept-language"))
    try:
        with use_translations(CATALOGS[language]):
            yield
    except Exception as exc:
        dependency_app.state.teardown.append(f"def: {type(exc).__name__}: {exc}")
        raise


@dependency_app.get("/async-dependency", dependencies=[Depends(bind_in_async_dependency)])
async def through_async_dependency(request: Request, name: str, n: int) -> Rendered:
    await request.app.state.pause()
    return render(name, n)


@dependency_app.get("/sync-dependency", dependencies=[Depends(bind_in_sync_dependency)])
async def through_sync_dependency(request: Request, name: str, n: int) -> Rendered:
    await request.app.state.pause()
    return render(name, n)
