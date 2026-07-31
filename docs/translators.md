---
description: "The placeholder contract for whoever edits the .po files: what you may change, what you must leave alone, and how to read the errors."
---

# For translators

This page is for the person editing the catalog, not the person writing the
code. It is short on purpose, and it is meant to be linked or copied into a
project's own translator instructions.

Nothing here requires you to read Python. Everything here is about one thing:
the pieces of a message in curly braces.

## What a placeholder is

A message in a catalog may contain names in curly braces:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` is a **placeholder**. When the program shows this message it replaces
`{name}` with a value it supplies — a person's name, a file name, a number. The
placeholder is not a word to translate; it is a slot.

Your translation goes in the `msgstr`, and it must keep that slot:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## What you may change, and what you may not

You **may**:

- **Move a placeholder** anywhere the target language's grammar wants it,
  including to the front of the message.
- **Repeat a placeholder** if the language needs the value twice.
- **Rewrite every other word**, including punctuation, spacing, and sentence
  order.

You **must not**:

- **Translate the name inside the braces.** `{name}` stays `{name}`, even in a
  language that writes nothing else in Latin letters.
- **Remove the braces**, or write the name without them.
- **Replace the ASCII braces `{` `}` with full-width `｛` `｝`.** Many input
  methods produce the full-width forms; they look almost identical and do not
  work.
- **Add formatting**, such as `{name!r}` or `{amount:.2f}`. How a value is
  displayed is decided in the program, not in the catalog.
- **Invent a placeholder** that is not in the `msgid`.

If a message needs a value the original does not offer, that is a message the
developer has to change. Say so rather than working around it.

## Plural forms

A counted message arrives with one `msgstr` slot per plural form in your
language, and your language decides how many that is — one for Japanese, two
for German, three for Russian, six for Arabic. Fill in every slot the catalog
gives you.

Two rules that catch people out:

- **The slots are not "singular, plural, more plural".** Each index means
  whatever your language's plural rule says it means. Latvian's third form is
  for zero alone; Slovenian's second is for exactly two; Welsh puts the general
  case at index 0 and the singular at index 1.
- **Two slots may legitimately hold the same text.** In Turkish, Hungarian,
  Persian and Bengali a noun stays singular after a numeral, so both forms of a
  counted message are the same string. That is correct, not a copy-and-paste
  slip.

The placeholder rules above apply to every form independently.

## Fuzzy entries

An entry marked `fuzzy` is a machine's guess: the developer changed the
original message, and the tooling paired the new text with your old
translation so you have somewhere to start.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

A fuzzy entry is **not used by the program** — it shows the untranslated
original instead — until someone revises the text and removes the `fuzzy`
marker. Most PO editors have a button for exactly that.

## Reading a failure message { #reading-a-failure-message }

The tooling checks placeholders when the catalog is compiled, and the message
is written for you rather than for a programmer. Reporting only that `{name}`
is missing is a dead end when you can see those characters in front of you, so
where a placeholder looks present but is not, the message says why. Against the
original `Hello {name}`, each of these is reported under
`translation does not match the source placeholders:`

| Your translation says | The reason it gives |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Characters that cannot be seen get their own treatment. A no-break space inside
the braces is something an input method produces and no editor shows, so the
message prints it by code point rather than naming a character you could never
find:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

A name whose letters mix writing systems — the homoglyph case, where a Cyrillic
`а` is indistinguishable from a Latin one — is shown twice, once readably and
once escaped, which is the only form that tells the two apart:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

The same disambiguation applies when a Greek or Cyrillic name written entirely
in one script conflicts with an ASCII source name, including the one-letter
Latin `a` / Cyrillic `а` case.

If you meet one of these and the fix is not obvious, the safe move is to delete
the placeholder you typed and copy the one from the `msgid`.

## What the checks cannot do

The tooling verifies that your placeholders are intact. It cannot tell whether
the translation is accurate, natural, or right for the context — that stays
entirely with you.

Two things help more than any check:

- **Read the translator comment.** A line beginning `#.` above the message is
  the developer telling you where it appears and what it means.
- **Ask about `msgctxt`.** When the same word appears twice with different
  contexts, it is because the two need to translate differently — "Open" the
  button and "Open" the state, for instance.
