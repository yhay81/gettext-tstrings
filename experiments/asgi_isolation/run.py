# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "babel==2.18.0",
#   "fastapi==0.143.3",
#   "gettext-tstrings",
#   "httpx==0.28.1",
# ]
#
# [tool.uv.sources]
# gettext-tstrings = { path = "../..", editable = true }
# ///
"""Drive app.py through a real ASGI request lifecycle and report what happened.

Run from the repository root:

    uv run experiments/asgi_isolation/run.py

Every request goes through httpx's in-process ASGI transport, which runs the
application in the calling task. That makes the binding observable from both
sides: inside a handler, and in the client's own context once the request has
finished, where anything the application failed to restore would still be
visible. Each client task binds a catalog of its own around the request for
exactly that reason. The exit status is non-zero when any expectation fails,
including the limitation the documentation describes, so that the day it stops
reproducing is a day the docs need to change.
"""

from __future__ import annotations

import asyncio
import functools
import gettext
import platform
import random
import sys
import threading
from collections import Counter
from collections.abc import Awaitable, Sequence
from importlib.metadata import version

import anyio.to_thread
import httpx
from app import LANGUAGES, Rendered, app, dependency_app

from gettext_tstrings import get_translations, use_translations

COMMAND = "uv run experiments/asgi_isolation/run.py"
OVERLAPPING = 200
# A catalog the client binds around each request. It must still be the binding
# when the request returns; the application's own binding must not be.
OUTER = gettext.NullTranslations()


def expected(language: str, name: str, n: int) -> Rendered:
    """What the catalogs say, written out independently of them."""
    if language == "ja":
        return {
            "bound": "ja",
            "hello": f"{name}さん、こんにちは",
            "files": f"ファイル{n}件",
            "label": "ようこそ",
        }
    return {
        "bound": "fr",
        "hello": f"Bonjour {name}",
        "files": f"{n} fichier" if n <= 1 else f"{n} fichiers",
        "label": "Bienvenue",
    }


def plan(count: int) -> list[tuple[str, str, int]]:
    """Both languages in equal numbers, in a fixed shuffled order, with values of their own.

    Not strictly alternating, on purpose. A binding shared between requests
    hands a request the value from two requests back on some paths, and strict
    alternation makes that the right language by coincidence: run against such a
    binding, the async-dependency check passed with ja, fr, ja, fr.
    """
    languages = [LANGUAGES[i % 2] for i in range(count)]
    random.Random(count).shuffle(languages)
    return [(language, f"user{i}", 1 + i % 3) for i, language in enumerate(languages)]


class Report:
    def __init__(self) -> None:
        self.failures = 0

    def check(self, label: str, failures: list[str], summary: str) -> None:
        if failures:
            self.failures += 1
            print(f"FAIL  {label}")
            for failure in failures[:5]:
                print(f"        {failure}")
        else:
            print(f"ok    {label}: {summary}")


async def request(
    client: httpx.AsyncClient, path: str, language: str, **params: str | int
) -> tuple[httpx.Response, bool]:
    """Send one request inside a binding of the client's own; report if it survived."""
    with use_translations(OUTER):
        response = await client.get(path, params=params, headers={"accept-language": language})
        restored = get_translations() is OUTER
    return response, restored


async def gather[T](calls: Sequence[Awaitable[T]]) -> list[T]:
    # A barrier that never fills would hang the run; fail it instead.
    async with asyncio.timeout(30):
        return list(await asyncio.gather(*calls))


async def overlapping_async(client: httpx.AsyncClient, report: Report) -> None:
    # Every handler renders, then waits at a barrier that opens only once all
    # of them are waiting, inside their own bindings, then renders again.
    barrier = asyncio.Barrier(OVERLAPPING)
    app.state.pause = barrier.wait
    requests = plan(OVERLAPPING)
    results = await gather(
        [request(client, "/greet", language, name=name, n=n) for language, name, n in requests]
    )
    failures = []
    for (language, name, n), (response, restored) in zip(requests, results, strict=True):
        want = expected(language, name, n)
        body = response.json() if response.status_code == 200 else None
        if body is None or body["before"] != want or body["after"] != want:
            failures.append(f"{language} {name}: {response.status_code} {response.text}")
        if not restored:
            failures.append(f"{language} {name}: the client's binding was not restored")
    report.check(
        f"{OVERLAPPING} overlapping async requests",
        failures,
        f"all {OVERLAPPING} were suspended inside their bindings at once; each rendered its "
        "own language and values before and after, and the client's binding was restored",
    )


async def overlapping_sync(client: httpx.AsyncClient, report: Report) -> None:
    # A two-party barrier holds each worker thread inside its request until a
    # second one arrives, so the requests overlap however the pool schedules.
    barrier = threading.Barrier(2, timeout=10)
    app.state.wait = barrier.wait
    limit = anyio.to_thread.current_default_thread_limiter().total_tokens
    requests = plan(100)
    results = await gather(
        [request(client, "/greet-sync", language, name=name, n=n) for language, name, n in requests]
    )
    failures = [
        f"{language} {name}: {response.status_code} {response.text}"
        for (language, name, n), (response, _) in zip(requests, results, strict=True)
        if response.status_code != 200 or response.json() != expected(language, name, n)
    ]
    failures += [
        f"request {i}: binding not restored" for i, (_, ok) in enumerate(results) if not ok
    ]
    report.check(
        "100 overlapping requests to a def endpoint",
        failures,
        f"each rendered its own language; the pool has at most {int(limit)} worker threads, "
        "so the threads were reused from one request to the next",
    )


async def after_the_response(client: httpx.AsyncClient, report: Report) -> None:
    # Both of these run after call_next has returned, so after the
    # middleware's `with` block has exited.
    app.state.background.clear()
    requests = plan(20)
    streamed = await gather(
        [request(client, "/stream", language, name=name, n=n) for language, name, n in requests]
    )
    failures = []
    for (language, name, n), (response, _) in zip(requests, streamed, strict=True):
        want = expected(language, name, n)
        if response.text != f"{want['bound']}|{want['hello']}|{want['label']}":
            failures.append(f"stream {language} {name}: {response.text}")
    await gather(
        [request(client, "/background", language, name=name, n=n) for language, name, n in requests]
    )
    rendered = Counter(tuple(sorted(item.items())) for item in app.state.background)
    wanted = Counter(tuple(sorted(expected(*r).items())) for r in requests)
    if rendered != wanted:
        failures.append(f"background tasks rendered {sorted(rendered)}")
    report.check(
        "streamed bodies and background tasks",
        failures,
        "20 of each rendered in their request's language after the middleware's block exited",
    )


async def failing_handlers(client: httpx.AsyncClient, report: Report) -> None:
    # The handlers fail while their bindings are active, overlapping each
    # other, and the exception unwinds through the middleware's `with` block.
    count = 20
    barrier = asyncio.Barrier(count)
    app.state.pause = barrier.wait
    app.state.failed_with.clear()
    languages = [language for language, _, _ in plan(count)]
    results = await gather([request(client, "/fail", language) for language in languages])
    failures = [
        f"status {response.status_code}" for response, _ in results if response.status_code != 500
    ]
    failures += [
        f"request {i}: binding not restored" for i, (_, ok) in enumerate(results) if not ok
    ]
    if Counter(app.state.failed_with) != Counter(languages):
        failures.append(f"handlers had bound {app.state.failed_with}")
    app.state.pause = functools.partial(asyncio.sleep, 0)
    after = plan(2)
    for language, name, n in after:
        response, restored = await request(client, "/greet", language, name=name, n=n)
        if response.json()["after"] != expected(language, name, n) or not restored:
            failures.append(f"after the failures, {language}: {response.text}")
    report.check(
        f"{count} overlapping requests whose handler raises",
        failures,
        "each answered 500 after raising inside its own binding, the client's binding was "
        "restored, and the next requests rendered normally",
    )


async def binding_in_dependencies(report: Report) -> None:
    transport = httpx.ASGITransport(app=dependency_app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://experiment") as client:
        requests = plan(20)
        dependency_app.state.pause = asyncio.Barrier(len(requests)).wait
        dependency_app.state.teardown.clear()
        results = await gather(
            [
                request(client, "/async-dependency", language, name=name, n=n)
                for language, name, n in requests
            ]
        )
        failures = [
            f"{language} {name}: {response.text}"
            for (language, name, n), (response, _) in zip(requests, results, strict=True)
            if response.json() != expected(language, name, n)
        ]
        failures += dependency_app.state.teardown
        report.check(
            "binding in an async def dependency with yield",
            failures,
            "20 requests suspended inside their bindings at once each rendered its own "
            "language, and every block was left cleanly",
        )

        dependency_app.state.pause = asyncio.Barrier(len(requests)).wait
        dependency_app.state.teardown.clear()
        results = await gather(
            [
                request(client, "/sync-dependency", language, name=name, n=n)
                for language, name, n in requests
            ]
        )
        unbound = [response.json()["bound"] for response, _ in results]
        english = [response.json()["hello"] for response, _ in results]
        errors = list(dependency_app.state.teardown)
        failures = []
        if any(code is not None for code in unbound):
            failures.append(f"the endpoint saw a binding after all: {unbound}")
        if english != [f"Hello {name}" for _, name, _ in requests]:
            failures.append(f"the endpoint did not render the source text: {english}")
        if len(errors) != len(requests) or not all(
            error.startswith("def: ValueError: ")
            and error.endswith("was created in a different Context")
            for error in errors
        ):
            failures.append(f"leaving the block did not raise as documented: {errors}")
        report.check(
            "LIMITATION, binding in a plain def dependency with yield",
            failures,
            "in all 20 the endpoint saw no binding and rendered the source text, and leaving "
            "the block raised ValueError because the token was created in a different Context",
        )


def versions() -> None:
    print(f"{'command':16} {COMMAND}")
    print(f"{'python':16} {platform.python_version()} ({sys.implementation.name})")
    for package in ("gettext-tstrings", "fastapi", "starlette", "httpx", "anyio", "babel"):
        print(f"{package:16} {version(package)}")
    print()


async def main() -> int:
    versions()
    report = Report()
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://experiment") as client:
        await overlapping_async(client, report)
        await overlapping_sync(client, report)
        await after_the_response(client, report)
        await failing_handlers(client, report)
    await binding_in_dependencies(report)
    print()
    print("all expectations held" if not report.failures else f"{report.failures} failed")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
