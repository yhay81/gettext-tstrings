---
description: "Thirty years of gettext, two PEPs ten years apart, and the stdlib discussion that closed as not-planned: why this library exists, with links to the sources."
---

# Background

This library sits at the meeting point of two long stories — one about how
software gets translated, one about how Python interpolates strings — that
finally intersected in 2025 and then stalled at exactly the point where a
small, careful convention was needed. This page tells both stories, with
links to the sources, because the design decisions on this site are easier to
judge when you can see the questions they answer.

## The gettext ecosystem { #the-gettext-ecosystem }

[GNU gettext] has been how free software gets translated since the mid-1990s:
mark the strings in code, extract them into a template, give translators one
catalog file per language, compile, load at runtime. Around that loop grew an
entire ecosystem — PO editors, review workflows, and translation platforms
that all speak the same file format — and Python has shipped a
[`gettext` module][stdlib-gettext] in its standard library for more than two
decades. The runtime half of translation was never the problem.

The unsettled half was always *what the catalog string looks like*. A
`%(name)s` message hands translators printf syntax that one deleted letter
turns into a production crash; a `.format()` message hands the catalog
attribute access on live objects. ([Why t-strings](comparison.md) walks
through both, with the failures on display.) And f-strings — the syntax most
Python code now prefers — cannot participate at all: by the time any library
sees one, it is already a finished string. People try anyway, often enough
that Babel's issue tracker collects the attempts
([#594][babel-594], [#715][babel-715]); the failure is structural, not a
missing feature.

## Two PEPs, ten years apart { #two-peps-ten-years-apart }

In 2015, Alyssa Coghlan and Nick Humrich wrote [PEP 501], proposing
interpolation templates whose stated first motivation was i18n — "providing a
cleaner syntax for i18n translation", in the PEP's own words. The proposal
was deferred, in part because discussion showed the i18n case carried
significant extra considerations that simpler use cases did not.

A decade later, [PEP 750] — by Jim Baker, Guido van Rossum, Paul Everitt,
Koudai Aono, Lysandros Nikolaou, and Dave Peck — revived the idea as
t-strings, was [accepted in April 2025][sc-resolution], and shipped in
[Python 3.14] in October 2025. PEP 501 was then withdrawn in its favour. One
detail matters for this page: i18n is *not* among PEP 750's stated
motivations. The PEP generalized the mechanism — a template type any library
can consume — and left the translation question exactly where PEP 501 had
parked it ten years earlier: open.

So as of Python 3.14, the language had precisely the data structure a message
catalog needs, and no convention for using it as one.

## The stdlib discussion { #the-stdlib-discussion }

Two months before 3.14 shipped, Adrian Mönnich (ThiefMaster, a maintainer of
the Indico project) proposed closing that gap in the standard library itself:
the thread [Support t-strings in gettext][discuss-thread] on
discuss.python.org, opened in August 2025, came with a working
[pull request][cpython-pr] adding t-string support to both `gettext` and
`pygettext`.

The thread is worth reading in full, because it surfaces every hard question
this library later had to answer:

- **What may an interpolation be?** A simple name only, or attributes and
  calls with a derived placeholder name? Every answer trades convenience
  against msgid stability and catalog safety.
- **What do plural forms require,** when the target language's plural system
  differs from the source's?
- **Is gettext even the right target?** Barry Warsaw — who had argued during
  PEP 750's development that t-strings were not a good fit for i18n — pointed
  to his [`flufl.i18n`][flufl-i18n] and its `$`-string style as the friendlier
  tool; others argued for leaving gettext behind entirely in favour of newer
  systems such as [Fluent].
- **And the meta-question:** whatever the standard library ships, it can
  essentially never change. A convention with this many open choices is a
  risky thing to freeze on the first try.

No consensus formed. The CPython issue was
[closed as "not planned"][cpython-issue] and the pull request was closed
unmerged in October 2025, days after 3.14's release. The capability existed
in the language; the convention had no home.

## Why a package, first { #why-a-package-first }

That is the gap this project chose to fill from outside the standard
library, on a deliberate wager: a convention matures faster where it can
version freely and earn adoption case by case, and the standard library —
which must be right the first time — is where a convention should *end up*,
not where it should be worked out.

Concretely, every contested question in the thread has a written-down answer
here, each on its own page:

- Interpolations are **simple names only**, so msgids stay stable and
  meaningful — [the guide](guide.md#safety-and-scope) shows the rule,
  [How it works](internals.md#from-template-to-msgid) the reasons.
- **Formatting stays out of the catalog** entirely
  ([Why t-strings](comparison.md)).
- **Plurals** follow a union/intersection rule that lets a target language's
  plural system differ from the source's ([spec §4](spec.md)).
- A broken catalog **falls back instead of crashing**, keeping gettext's own
  contract ([the guide](guide.md#what-happens-when-a-catalog-is-wrong)).
- And the whole convention is a [versioned specification](spec.md) with a
  machine-readable conformance suite — written so that another
  implementation, including a future standard-library one, could adopt it
  unchanged and interoperate.

The discussion has not ended, and this project is a participant in it, not a
verdict on it. If you have production gettext experience that bears on these
choices, the [same thread][discuss-thread] and this repository's
[Discussions][gh-discussions] are where it is argued.

## Timeline { #timeline }

| When | What happened |
| --- | --- |
| mid-1990s | GNU gettext establishes the PO/POT/MO workflow that translators and platforms still speak. |
| 2015 | [PEP 501] proposes interpolation templates, with i18n as its first motivation; deferred. |
| 2016 | f-strings ship in Python 3.6 — interpolation gets its syntax, and translation cannot use it. |
| Jul 2024 | [PEP 750] proposes t-strings. |
| Apr 2025 | PEP 750 [accepted][sc-resolution]; PEP 501 withdrawn in its favour. |
| Aug 2025 | The [Support t-strings in gettext][discuss-thread] thread opens, with a stdlib [pull request][cpython-pr]. |
| Oct 2025 | [Python 3.14] ships t-strings; the stdlib issue closes as [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` ships as an alpha, with [spec v1](spec.md) and its conformance suite. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
