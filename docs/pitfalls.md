---
description: "What translating one small site into thirty-five languages actually breaks, which of those the library can catch for you, and which it cannot."
---

# Pitfalls

This site is translated into thirty-five languages, and every one of them was
produced by running the loop this documentation teaches. That is a small
corpus by industry standards and it was still enough to hit most of the traps
that make i18n harder than it looks.

Each section below is something that actually went wrong here, what it looked
like at the time, and where the line falls between what the library checks for
you and what stays your judgement.

## Renaming a variable retranslates a sentence { #renaming-a-variable-retranslates-a-sentence }

The msgid is the catalog key, and an interpolated name is *inside* it. Moving
one constant to module scope and capitalising it the way Python style asks —
`author` to `AUTHOR` — changed `Copyright © 2026 {author} · MIT License` into a
message no catalog had ever seen. Every translation of that line would have
gone back through the fuzzy cycle, in every language, for a rename that changed
nothing a reader could see.

The library will not stop you: both spellings are valid placeholder names.
What it does do is make the name *worth* protecting — an interpolation has to
be a [plain name](internals.md#from-template-to-msgid), so the thing in the
catalog key is a word a translator can read, not an expression.

The mirror case is safe by construction. Conversions and format specs are not
part of the msgid, so tightening `{amount:,.2f}` to `{amount:,.0f}` changes no
key and invalidates no translation anywhere.

## `nplurals=2` does not mean two different strings { #nplurals-2-does-not-mean-two-different-strings }

Turkish, Hungarian, Persian and Bengali all declare two plural forms, and in
all four the two forms of a counted message are legitimately the *same string*
— the noun stays singular after a numeral, so `{n} sayfa` is right for one page
and for ten. A reviewer who "fixes" the duplication breaks the translation.

The opposite mistake is just as easy. Latvian's third form exists for **zero
alone**; Slovenian's second is a **dual**, for exactly two; Romanian's last form
requires the word `de` that its first two must not have. Filling those slots
with a singular and a plural produces a catalog that is wrong only for counts
nobody tests.

Worse, the *order* of the slots is not semantic. Welsh indexes its five forms
so that `msgstr[0]` is the general case and `msgstr[1]` is the singular.
Filling them in the obvious sequence puts the singular where every uncounted
message will find it.

The library takes none of this on itself, and that is the point: the target
language's plural rule lives in its own catalog header, and the
[union/intersection rule](spec.md) lets a translation have more forms, or
fewer, than the source. What it checks is the only thing it can check without
knowing the language — that every form keeps the placeholders it needs.

## Two forms can be identical for a reason { #two-forms-can-be-identical-for-a-reason }

Irish has five plural forms, and in this site's build report several of them
are spelled the same. That is not a copy-paste slip: *leathanach* begins with
`l`, and neither of the initial mutations Irish numerals trigger is written on
`l`. The forms still do real work — the stem alternates between *leathanach*
and *leathanaigh*, and counts above ten revert to the singular — but no noun
meaning "page" would show the contrast.

Any check that flags duplicate forms as suspicious will flag correct Irish.
A human who knows the language is the only reviewer for this.

## A message can only agree with one count { #a-message-can-only-agree-with-one-count }

This site's build report says how many pages were rendered and how long it
took. Writing it as "Rendered {n} pages in {seconds} seconds" looks harmless
and is not translatable: gettext selects one form from one count, and that
count is `n`. The word *seconds* would have to agree with a number the plural
machinery never sees.

The fix is to make the second quantity a unit symbol rather than a word, and
unit symbols are themselves localised: this site's catalogs carry `s`, `с`,
`ث`, `שנ׳` and `mp`, and French, Spanish and Swedish typography wants a space
before the symbol where English does not. None of that is the library's
business — but noticing that a message needs *two* agreements is, and the only
tool for it is writing the message differently.

## Editing an English sentence edits foreign grammar { #editing-an-english-sentence-edits-foreign-grammar }

The home page used to say "all ten language editions". Removing the number —
a one-word English edit, made because the number kept going stale — turned a
plural subject singular. Spanish, Italian, Portuguese, Russian, Ukrainian,
Greek, Dutch and Hebrew all had to re-agree the verb; several needed the
participle changed too.

A source edit that reads as trivial in English is not trivial downstream.
Marking it fuzzy, which is what `pybabel update` does, is the mechanism that
gives each translator the chance to notice.

## Invisible differences survive every copy-paste { #invisible-differences-survive-every-copy-paste }

The guide quotes a diagnostic containing `(nаme)` — a deliberate escape,
because the character it names is a Cyrillic `а` that no reader can tell from
the Latin one. Translators of this site converted that escape into the actual
character **five separate times**, in five different languages, each time
producing a page that looked correct and was wrong.

This one the library does catch, and it is the reason the diagnostics are
shaped the way they are: a placeholder whose letters mix writing systems is
[reported twice](internals.md#diagnostics-are-part-of-the-design), once
readably and once escaped, because the escaped form is the only spelling that
distinguishes them. A no-break space inside braces is printed by code point
for the same reason. The catalog checker refuses the message before it can
ship.

## Non-empty is not translated { #non-empty-is-not-translated }

A catalog scaffolded with its msgids copied into the msgstrs passes every
naive check: nothing is empty, nothing is fuzzy, the message set matches
exactly. One edition of this site shipped that way for several hours. So did
eight pages of another edition that were byte-identical copies of the English
source — which passes a check comparing code blocks between them, because they
are the same file.

Neither is something a translation library can see. Both are cheap to test for
once you know to: compare against the source and require a difference.

## The catalog is not the only translated thing { #the-catalog-is-not-the-only-translated-thing }

Two failures here had nothing to do with gettext.

Translating a heading changes the anchor generated from it, so every
cross-page link into that section breaks — silently, in that language only.
This site pins the English anchor on every heading, and a test derives the
expected list from the English page.

And the site generator ships interface translations for sixty-eight
languages, which does not include Swahili or Irish. Without one the build does
not degrade to English; the template include fails and the edition cannot be
built at all. Two of this repository's own files exist to fill that gap.

## Your tools have bugs too { #your-tools-have-bugs-too }

The CI step this documentation recommends for catching stale catalogs,
`pybabel update --check`, cannot do that job for any project that uses
`pgettext` or `npgettext` — it reports every catalog with a `msgctxt` as out
of date, on every run, because of a bug in how the comparison looks messages
up. It was found here by trying to use it, reported upstream, and is
[described in full with the workaround](workflow.md#what-ci-gates).

The general lesson is the uncomfortable one: a gate that is always red is
worse than no gate, because a team turns it off. Verify that your CI check can
actually pass before you trust it to fail.

## What the library is for, in one line { #what-the-library-is-for-in-one-line }

Most of this page is judgement no tool can take over. What a tool *can* do is
guarantee that a translation cannot change the structure of the sentence it
translates — cannot drop a value, invent one, reformat one, or reach into your
objects — and can say so in a sentence the person who has to fix it can act
on. That is the whole of what this library promises, and the rest of this site
is how it keeps it.
