# Runtime microbenchmarks

`runtime.py` times the render path next to two references that never touch
this package, an f-string and `gettext(...).format(...)`, so that its cost can
be read against what an application pays anyway.

| Case | What it times |
| --- | --- |
| `f-string` | `f'Hello {name}'`: no translation at all, the floor |
| `gettext(str).format` | the `str.format` idiom this package replaces |
| `compiled.render` | rendering a precompiled template, with no catalog lookup |
| `compile_template` | compiling a template whose plan is already cached |
| `tr (1 field)`, `tr (2 fields)` | the module-level function, with one and two placeholders |
| `Translator (1 field)` | a bound translator, called the way `_` is |
| `ngettext (1 field)` | the plural path, `ntr` |

## Running it

```console
uv run python benchmarks/runtime.py
```

prints the table. `--json FILE` also writes a machine-readable record of the
same run, and `--markdown FILE` appends a summary table to a file such as
`$GITHUB_STEP_SUMMARY`:

```console
uv run python benchmarks/runtime.py --json benchmark.json
```

A record made on your machine compares only with other records from your
machine.

## The Benchmark workflow

`.github/workflows/benchmark.yml` runs the same command in one fixed
environment: GitHub's `ubuntu-24.04` image, CPython 3.14 as setup-uv installs
it, and the package without its development dependencies. It uploads the
record as an artifact named `benchmark-<commit>` and shows the table in the job
summary. It never starts on its own. Dispatch it from the Actions tab, or:

```console
gh workflow run benchmark.yml --ref <branch>
gh run download <run-id> --name benchmark-<commit>
```

Nothing fails on timing, there or in CI. On a shared runner any threshold turns
noise into red builds, and CI's own benchmark step only checks that the script
still runs.

## What a record holds

| Field | Meaning |
| --- | --- |
| `schema` | `1`; bumped when a field changes meaning |
| `recorded_at` | UTC time of the run |
| `commit.sha`, `commit.dirty` | the commit measured, and whether tracked files differed from it |
| `python` | `version`, `implementation`, `free_threaded`, and the `compiler` that built the interpreter |
| `machine` | `system`, `release`, `architecture`, the `cpu` model, `cpu_count`, and on a hosted runner the `runner_image` and its version |
| `settings` | `number` of calls per sample, `repeat` count, the `timer`, the `statistic`, and the `warm_up` |
| `results` | per case: `name`, the timed `statement`, `median_ns`, and every sample in `samples_ns` |

## How the numbers are taken

- **Warm-up.** Each cached path is called once before anything is timed, so the
  cases measure the steady state an application reaches after its first
  request. First-call compilation is not part of any case.
- **Repeats.** `timeit` times each case 7 times, 100,000 calls per sample,
  using `time.perf_counter` with the garbage collector off. The reported figure
  is the median of the 7 per-call times, and the record keeps all 7, so the
  spread within one run is visible too.

## Comparing two commits

A single number from a hosted runner says more about the runner than about the
code. Runs of one image land on different CPU models, and other tenants on a
host come and go. For a comparison to mean something:

1. **Compare like with like.** Use records with the same `machine.cpu`,
   `python.version` and `python.free_threaded`. Records from different CPU
   models do not compare in nanoseconds at all.
2. **Read ratios, not nanoseconds.** Divide each case by the `f-string` and
   `gettext(str).format` medians of the same record. Those two depend only on
   the machine and the interpreter, so the ratio cancels most of a runner's
   speed. The job summary shows the ratio to the f-string.
3. **Repeat.** Dispatch the workflow three times for each commit. Treat a
   slowdown as real only if all three ratios of the newer commit are above all
   three of the older one. With no real change, that happens by chance once in
   20 comparisons, and the same holds for a speedup.
4. **Then decide whether it matters.** A few percent on a path that costs a few
   hundred nanoseconds is rarely worth chasing. A sustained change of 10% or
   more on `tr` or `Translator`, the paths applications call most, is worth
   investigating, and so is any change in which case is faster than which.

Records worth keeping are checked in under `results/`, named
`<date>-<commit>.json`, so that a later comparison has something to start from.
