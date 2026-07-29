Here is the technical overview and production-grade Python solution to validate per-request translation isolation in a real ASGI application using `contextvars`.

---

### Technical Overview

#### Problem & Root Cause
In asynchronous Python (ASGI) web frameworks (e.g., Starlette, FastAPI, Quart), multiple HTTP requests are handled concurrently within the same OS process on a single event loop. Global state (e.g., global module variables) leaks across concurrent requests. Traditional `gettext` approaches that mutate thread-local or global state fail in ASGI because async tasks switch context on the same thread during I/O yields.

#### Solution Architecture
`ContextVar` objects from Python's standard `contextvars` module provide task-local storage. When an asyncio task yields execution (e.g., `await asyncio.sleep(...)` or database/network I/O), Python preserves the active `ContextVar` context for that specific execution chain.

1. **Context Management Layer**:
   - `_current_language`: A `ContextVar[str]` storing the ISO language code for the current request context.
   - `_current_translation`: A `ContextVar[gettext.NullTranslations]` storing the compiled translation catalog for the request context.
   - `set_language()` / `reset_language()`: Utility functions managing context state transition tokens safely.

2. **ASGI Middleware Layer (`ASGITranslationMiddleware`)**:
   - Intercepts incoming HTTP requests in the ASGI call chain.
   - Parses the target language from the `Accept-Language` header or `lang` query string parameter.
   - Activates the request-specific translation catalog using `ContextVar.set()`.
   - Uses a `try ... finally` block to guarantee context token cleanup (`ContextVar.reset()`) regardless of unhandled exceptions or early returns.

3. **Validation Strategy**:
   - A real ASGI app handles concurrent requests with artificial async delay variations (`await asyncio.sleep(...)`) injected during request processing.
   - Multiple concurrent clients execute interleaved requests across different languages (`en`, `es`, `fr`, `de`).
   - Asserts 100% translation context fidelity across all concurrent responses without cross-task contamination or race conditions.

---

### Implementation

```python
import asyncio
import gettext
import io
from contextvars import ContextVar, Token
from typing import Dict, Tuple, Optional
from httpx import AsyncClient, ASGITransport

# ============================================================================
# 1. Translation Context & Storage Engine (gettext-tstrings integration)
# ============================================================================

# Default fallback language
DEFAULT_LANGUAGE = "en"

# ContextVar storage for per-request task-local context
_current_language: ContextVar[str] = ContextVar("current_language", default=DEFAULT_LANGUAGE)
_current_translation: ContextVar[gettext.NullTranslations] = ContextVar(
    "current_translation", default=gettext.NullTranslations()
)

# Mock translation catalogs for validation (simulates compiled .mo files)
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "Hello, World!": "Hello, World!",
        "Goodbye": "Goodbye",
    },
    "es": {
        "Hello, World!": "¡Hola, Mundo!",
        "Goodbye": "Hasta luego",
    },
    "fr": {
        "Hello, World!": "Bonjour le monde!",
        "Goodbye": "Au revoir",
    },
    "de": {
        "Hello, World!": "Hallo Welt!",
        "Goodbye": "Auf Wiedersehen",
    },
}


class DictTranslations(gettext.NullTranslations):
    """Custom Translation class backed by a dictionary catalog."""

    def __init__(self, catalog: Dict[str, str]):
        super().__init__()
        self._catalog = catalog

    def gettext(self, message: str) -> str:
        return self._catalog.get(message, message)


# Pre-instantiated translation objects per language
CATALOGS: Dict[str, gettext.NullTranslations] = {
    lang: DictTranslations(mapping) for lang, mapping in TRANSLATIONS.items()
}


def set_language(lang: str) -> Tuple[Token, Token]:
    """
    Sets the current language and translation catalog for the active async task context.
    Returns ContextVar Tokens required for proper scope teardown.
    """
    selected_lang = lang if lang in CATALOGS else DEFAULT_LANGUAGE
    catalog = CATALOGS[selected_lang]

    token_lang = _current_language.set(selected_lang)
    token_trans = _current_translation.set(catalog)
    return token_lang, token_trans


def reset_language(tokens: Tuple[Token, Token]) -> None:
    """Resets language ContextVars back to their state prior to request processing."""
    token_lang, token_trans = tokens
    _current_language.reset(token_lang)
    _current_translation.reset(token_trans)


def get_language() -> str:
    """Retrieve current request's active language code."""
    return _current_language.get()


def _(message: str) -> str:
    """Translate string using current task's active context."""
    return _current_translation.get().gettext(message)


# ============================================================================
# 2. ASGI Middleware for Per-Request Context Management
# ============================================================================

class ASGITranslationMiddleware:
    """
    ASGI Middleware that extracts language preference from HTTP request headers
    or query parameters and binds it to the current contextvar lifecycle.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        lang = self._extract_language(scope)
        tokens = set_language(lang)

        try:
            await self.app(scope, receive, send)
        finally:
            reset_language(tokens)

    def _extract_language(self, scope) -> str:
        # Check query string parameter 'lang'
        query_string = scope.get("query_string", b"").decode("utf-8")
        for param in query_string.split("&"):
            if param.startswith("lang="):
                return param.split("=")[1].lower()

        # Check Accept-Language header
        headers = dict(scope.get("headers", []))
        accept_lang = headers.get(b"accept-language", b"").decode("utf-8")
        if accept_lang:
            # Primary language subtag
            primary = accept_lang.split(",")[0].split(";")[0].strip().lower()
            if primary in CATALOGS:
                return primary

        return DEFAULT_LANGUAGE


# ============================================================================
# 3. Sample ASGI Endpoint Application
# ============================================================================

async def demo_asgi_app(scope, receive, send):
    """
    ASGI Application handler simulating real-world async I/O work (e.g. DB queries)
    to test task switching and context isolation stability.
    """
    if scope["type"] == "http":
        current_lang = get_language()
        
        # Introduce variable async delay to force event loop task interleaving
        delay = 0.05 if current_lang in ("es", "de") else 0.02
        await asyncio.sleep(delay)

        # Retrieve translations within active context
        translated_greeting = _("Hello, World!")
        translated_farewell = _("Goodbye")

        # Verify internal context consistency mid-request
        active_lang_after_yield = get_language()
        assert current_lang == active_lang_after_yield, (
            f"Context leak detected! Started with {current_lang}, became {active_lang_after_yield}"
        )

        response_body = f"{current_lang}|{translated_greeting}|{translated_farewell}".encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/plain; charset=utf-8"],
                [b"content-length", str(len(response_body)).encode("utf-8")],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response_body,
        })


# ============================================================================
# 4. Concurrency Test & Isolation Validation Suite
# ============================================================================

async def run_concurrency_validation():
    """
    Executes multiple parallel requests across different languages concurrently
    to validate zero cross-talk in ASGI context handling.
    """
    app = ASGITranslationMiddleware(demo_asgi_app)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        test_cases = [
            ("es", "¡Hola, Mundo!", "Hasta luego"),
            ("fr", "Bonjour le monde!", "Au revoir"),
            ("de", "Hallo Welt!", "Auf Wiedersehen"),
            ("en", "Hello, World!", "Goodbye"),
            ("es", "¡Hola, Mundo!", "Hasta luego"),
            ("de", "Hallo Welt!", "Auf Wiedersehen"),
            ("fr", "Bonjour le monde!", "Au revoir"),
            ("en", "Hello, World!", "Goodbye"),
        ]

        async def make_request(requested_lang: str, expected_greeting: str, expected_farewell: str):
            # Interleave request types using query params and Accept-Language headers
            if hash(requested_lang) % 2 == 0:
                response = await client.get(f"/?lang={requested_lang}")
            else:
                response = await client.get("/", headers={"accept-language": requested_lang})

            assert response.status_code == 200
            res_lang, res_greeting, res_farewell = response.text.split("|")

            assert res_lang == requested_lang, f"Expected lang {requested_lang}, got {res_lang}"
            assert res_greeting == expected_greeting, f"Expected greeting {expected_greeting}, got {res_greeting}"
            assert res_farewell == expected_farewell, f"Expected farewell {expected_farewell}, got {res_farewell}"
            return True

        # Run all requests simultaneously to saturate event loop concurrency
        tasks = [make_request(lang, greeting, farewell) for lang, greeting, farewell in test_cases]
        results = await asyncio.gather(*tasks)

        print(f"✅ Successfully validated {len(results)} concurrent ASGI requests.")
        print("✅ Translation context isolation verified: ZERO cross-request contamination.")


if __name__ == "__main__":
    asyncio.run(run_concurrency_validation())
```