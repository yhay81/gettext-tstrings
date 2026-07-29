# Governance

`gettext-tstrings` uses lightweight, maintainer-led governance. Decisions are
public by default and the specification is treated as a shared interoperability
contract rather than an implementation detail.

## Roles

- **Contributors** report problems, join Discussions, improve documentation,
  code, tests, translations, or the conformance suite.
- **Reviewers** are trusted contributors who regularly review changes in an
  area they understand.
- **Maintainers** merge changes, publish releases, manage security reports, and
  are accountable for the health of the project.

Yusuke Hayashi is the current maintainer.

## Decisions

Routine fixes are decided in pull-request review. New public APIs, changes to
the t-string ↔ msgid convention, and backwards-incompatible behavior start in an
Issue or Discussion so users and tool authors can comment before code is merged.

Maintainers seek rough consensus and explain the final decision. When trade-offs
remain, the priorities are:

1. translation safety and predictable failure behavior;
2. compatibility with Python gettext and existing catalogs;
3. a small, teachable specification;
4. measurable runtime and extraction performance;
5. convenience that does not weaken the first four.

## Becoming a reviewer or maintainer

There is no contribution quota. A contributor may be invited to review or
maintain when they have shown sustained sound judgment, constructive review,
respect for the project's scope, and willingness to uphold the
[Code of Conduct](CODE_OF_CONDUCT.md).

Roles can be declined or relinquished at any time. Maintainer changes are
announced in Discussions and recorded in this file.
