# Per-request isolation in a real ASGI app

**The claim.** One process can serve several languages at once. Binding each
request's catalog with `use_translations()` in an ASGI middleware, as
[*In production*](../../docs/workflow.md#binding-a-language-at-runtime)
recommends, keeps every request in its own language and leaves nothing behind
when the request ends, whether it returns or raises.
`tests/test_runtime_binding.py` proves the primitive with bare asyncio tasks
([#10](https://github.com/yhay81/gettext-tstrings/issues/10)); this experiment
checks the boundary applications actually depend on
([#13](https://github.com/yhay81/gettext-tstrings/issues/13)).

## Run it

From the repository root:

```console
uv run experiments/asgi_isolation/run.py
```

uv reads the dependencies from the inline metadata at the top of `run.py`, takes
their exact versions from `run.py.lock`, and installs this checkout of
gettext-tstrings into the experiment's own environment. Nothing reaches the
package's dependencies or `uv.lock`. The exit status is 0 when every
expectation below holds, and the run takes about a second.

## What it does

`app.py` is a FastAPI application written the way the documentation writes it:
a Japanese and a French catalog (`locales/`, compiled in memory at import), an
HTTP middleware that binds the negotiated one around `call_next`, and a
`lazy_gettext` label defined at module level. Its only concession to the
experiment is `app.state.pause` and `app.state.wait`, the points where a real
handler would wait on I/O, which `run.py` replaces with barriers.

`run.py` sends requests through httpx's in-process ASGI transport. That
transport runs the application in the calling task, so a binding is visible
from both sides: inside the handler, and in the client's own context after the
request has returned, where anything the application failed to restore would
still be in place. Each client request is therefore made inside a binding of
the client's own, which must survive it.

| Check | What has to hold |
| --- | --- |
| 200 overlapping requests to an `async def` endpoint | Each handler renders, waits at a barrier that opens only once all 200 are suspended inside their bindings, and renders again. Both renders are in the request's language with the request's own values: `Hello {name}`, a plural, and the module-level label. The client's binding is restored. |
| 100 overlapping requests to a `def` endpoint | FastAPI runs these on AnyIO's pool of at most 40 worker threads, so threads are reused across requests, and a two-party barrier keeps every handler waiting inside its binding for another. Each renders its own request's language. |
| Streamed bodies and background tasks | Both run after `call_next` has returned, so after the middleware's `with` block has exited. Both render in the request's language. |
| 20 overlapping requests whose handler raises | Each raises inside its binding and answers 500. The client's binding is restored, and the next requests render normally. |
| Binding in an `async def` dependency with `yield` | 20 requests suspended inside their bindings at once each render their own language, and every block exits cleanly. |
| **Limitation**: binding in a plain `def` dependency with `yield` | In all 20 the endpoint sees no binding and renders the source text, and leaving the block raises `ValueError`. |

The languages come in equal numbers in a fixed shuffled order rather than
strictly alternating. To check that the experiment can fail, it was run against
a binding shared between requests: with strict alternation, the
`async def`-dependency check still passed, because on that path a shared
binding hands each request the value from two requests back. With the shuffled
order, all six checks fail.

## Result

Recorded on 2026-10-18 on macOS 27.0.1, arm64, with uv 0.13.1:

```text
command          uv run experiments/asgi_isolation/run.py
python           3.14.8 (cpython)
gettext-tstrings 0.1.0a8
fastapi          0.143.3
starlette        1.8.0
httpx            0.28.1
anyio            4.15.1
babel            2.18.0

ok    200 overlapping async requests: all 200 were suspended inside their bindings at once; each rendered its own language and values before and after, and the client's binding was restored
ok    100 overlapping requests to a def endpoint: each rendered its own language; the pool has at most 40 worker threads, so the threads were reused from one request to the next
ok    streamed bodies and background tasks: 20 of each rendered in their request's language after the middleware's block exited
ok    20 overlapping requests whose handler raises: each answered 500 after raising inside its own binding, the client's binding was restored, and the next requests rendered normally
ok    binding in an async def dependency with yield: 20 requests suspended inside their bindings at once each rendered its own language, and every block was left cleanly
ok    LIMITATION, binding in a plain def dependency with yield: in all 20 the endpoint saw no binding and rendered the source text, and leaving the block raised ValueError because the token was created in a different Context

all expectations held
```

Three consecutive runs printed exactly this.

## The verified pattern, and where it stops

- **Bind in middleware, around `call_next`.** The documented example works as
  written, for `async def` and `def` endpoints alike.
- **Work that outlives `call_next` keeps the request's language.** Streamed
  bodies and background tasks run in the task that Starlette started for the
  rest of the request, which received a copy of the request's context while the
  binding was in place. Leaving the middleware's block does not reach into that
  copy.
- **`def` endpoints get the binding too.** FastAPI calls them through AnyIO's
  thread pool, which runs each call in a copy of the caller's context. A bare
  `threading.Thread` promises no such thing; see
  [*Guide*](../../docs/guide.md#several-languages-at-once).
- **An `async def` dependency with `yield` is also a fine place to bind.**
- **A plain `def` dependency with `yield` is not.** FastAPI runs its setup and
  its teardown as separate calls into the thread pool, each in its own copy of
  the context. The binding made during setup never reaches the endpoint, so the
  page renders in the source language, and the reset during teardown raises
  `ValueError: <Token …> was created in a different Context`. The response is
  still a 200, so the failure shows up only in the logs and in the wrong
  language.

What this does not cover: a network server. The in-process transport runs the
application in the caller's task, which is what makes the client-side checks
possible. A server such as Uvicorn gives each request a task of its own instead.
