# Experiments

An experiment checks one claim the documentation makes against the real
third-party software the claim depends on, and records what happened: the
versions, the exact command, the output. The test suite cannot do that without
making every contributor and every CI job install that software, so each
experiment carries its own dependencies instead, in inline script metadata
pinned by a lock file next to the script. CI does not run them, and the package
never depends on anything they install.

| Experiment | Claim | Issue |
| --- | --- | --- |
| [`asgi_isolation`](asgi_isolation/) | Per-request bindings stay isolated through a real ASGI request lifecycle, under FastAPI. | [#13](https://github.com/yhay81/gettext-tstrings/issues/13) |
| [`weblate_round_trip`](weblate_round_trip/) | A catalog survives import, translation and export in Weblate, and Weblate's check works on it, with two documented differences. | [#15](https://github.com/yhay81/gettext-tstrings/issues/15) |

## Running and changing one

From the repository root, `uv run experiments/<name>/run.py` builds the
experiment's environment from its lock file, with this checkout of
gettext-tstrings installed editable, and runs it. A non-zero exit status means
an expectation failed. Anything an experiment needs beyond uv, such as the
PostgreSQL server the Weblate one starts, is listed in its README.

An experiment may have a second script with an environment of its own:
`weblate_round_trip` runs Weblate from `weblate_side.py`, with Weblate's own
pinned dependencies on Python 3.12. Lock and check each script the same way.
After changing a script's dependencies, refresh its lock:

```console
uv lock --script experiments/<name>/run.py
```

The project's `ty check` skips this directory, because the project environment
does not have an experiment's dependencies. Check an experiment in its own
environment instead:

```console
uv run ty check --python "$(uv python find --script experiments/<name>/run.py)" \
    --extra-search-path experiments/<name> experiments/<name>
```

When an experiment's versions change, run it again and replace the recorded
result in its README.
