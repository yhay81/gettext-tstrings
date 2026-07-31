---
description: "Der Platzhalter-Vertrag für alle, die die .po-Dateien bearbeiten: was du ändern darfst, was du unangetastet lassen musst und wie die Fehlermeldungen zu lesen sind."
---

# Für Übersetzende

Diese Seite richtet sich an die Person, die den Katalog bearbeitet, nicht an
die, die den Code schreibt. Sie ist mit Absicht kurz und dafür gedacht,
verlinkt oder in die eigenen Übersetzungshinweise eines Projekts kopiert zu
werden.

Nichts hier verlangt, dass du Python lesen kannst. Alles hier dreht sich um
eine einzige Sache: die Teile einer Nachricht in geschweiften Klammern.

## Was ein Platzhalter ist { #what-a-placeholder-is }

Eine Nachricht in einem Katalog kann Namen in geschweiften Klammern enthalten:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` ist ein **Platzhalter**. Wenn das Programm diese Nachricht anzeigt,
ersetzt es `{name}` durch einen Wert, den es liefert — einen Personennamen,
einen Dateinamen, eine Zahl. Der Platzhalter ist kein Wort zum Übersetzen; er
ist eine Leerstelle.

Deine Übersetzung kommt in das `msgstr`, und sie muss diese Leerstelle
behalten:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Was du ändern darfst und was nicht { #what-you-may-change-and-what-you-may-not }

Du **darfst**:

- **Einen Platzhalter verschieben**, überallhin, wo die Grammatik der
  Zielsprache ihn haben will, auch an den Anfang der Nachricht.
- **Einen Platzhalter wiederholen**, wenn die Sprache den Wert zweimal
  braucht.
- **Jedes andere Wort umschreiben**, einschließlich Zeichensetzung, Leerraum
  und Satzstellung.

Du **darfst nicht**:

- **Den Namen in den Klammern übersetzen.** `{name}` bleibt `{name}`, auch in
  einer Sprache, die sonst nichts in lateinischen Buchstaben schreibt.
- **Die Klammern entfernen** oder den Namen ohne sie schreiben.
- **Die ASCII-Klammern `{` `}` durch vollbreite `｛` `｝` ersetzen.** Viele
  Eingabemethoden erzeugen die vollbreiten Formen; sie sehen fast identisch
  aus und funktionieren nicht.
- **Formatierung hinzufügen**, etwa `{name!r}` oder `{amount:.2f}`. Wie ein
  Wert dargestellt wird, entscheidet das Programm, nicht der Katalog.
- **Einen Platzhalter erfinden**, der nicht im `msgid` steht.

Wenn eine Nachricht einen Wert braucht, den das Original nicht anbietet, dann
ist das eine Nachricht, die die entwickelnde Person ändern muss. Sag Bescheid,
statt es zu umgehen.

## Pluralformen { #plural-forms }

Eine gezählte Nachricht kommt mit einer `msgstr`-Leerstelle pro Pluralform
deiner Sprache, und deine Sprache entscheidet, wie viele das sind — eine im
Japanischen, zwei im Deutschen, drei im Russischen, sechs im Arabischen. Fülle
jede Leerstelle aus, die der Katalog dir gibt.

Zwei Regeln, an denen viele scheitern:

- **Die Leerstellen sind nicht „Singular, Plural, noch mehr Plural“.** Jeder
  Index bedeutet das, was die Pluralregel deiner Sprache sagt. Die dritte Form
  des Lettischen gilt allein der Null, die zweite des Slowenischen genau der
  Zwei, und das Walisische stellt den allgemeinen Fall auf Index 0 und den
  Singular auf Index 1.
- **Zwei Leerstellen dürfen legitim denselben Text enthalten.** Im Türkischen,
  Ungarischen, Persischen und Bengalischen bleibt ein Substantiv nach einem
  Zahlwort im Singular, sodass beide Formen einer gezählten Nachricht derselbe
  String sind. Das ist richtig so und kein Copy-Paste-Fehler.

Die obigen Platzhalterregeln gelten für jede Form einzeln.

## fuzzy-Einträge { #fuzzy-entries }

Ein als `fuzzy` markierter Eintrag ist die Vermutung einer Maschine: Die
entwickelnde Person hat die Originalnachricht geändert, und das Werkzeug hat
den neuen Text mit deiner alten Übersetzung gepaart, damit du einen
Anfangspunkt hast.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Ein fuzzy-Eintrag wird **vom Programm nicht verwendet** — es zeigt stattdessen
das unübersetzte Original —, bis jemand den Text überarbeitet und die
`fuzzy`-Markierung entfernt. Die meisten PO-Editoren haben genau dafür eine
Schaltfläche.

## Fehlermeldungen lesen { #reading-a-failure-message }

Die Werkzeuge prüfen die Platzhalter beim Kompilieren des Katalogs, und die
Meldung ist für dich geschrieben, nicht für eine programmierende Person. Nur
zu melden, dass `{name}` fehlt, ist eine Sackgasse, wenn du genau diese
Zeichen vor dir siehst — wo ein Platzhalter also vorhanden aussieht, es aber
nicht ist, sagt die Meldung warum. Gegen das Original `Hello {name}` wird
jeder der folgenden Fälle unter
`translation does not match the source placeholders:` gemeldet:

| Deine Übersetzung enthält | Der genannte Grund |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Zeichen, die man nicht sehen kann, bekommen eine eigene Behandlung. Ein
geschütztes Leerzeichen innerhalb der Klammern ist etwas, das eine
Eingabemethode erzeugt und das kein Editor anzeigt; die Meldung gibt es
deshalb als Codepoint aus, statt ein Zeichen zu benennen, das du nie finden
könntest:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ein Name, dessen Buchstaben Schriftsysteme mischen — der Homoglyphenfall, in
dem ein kyrillisches `а` von einem lateinischen nicht zu unterscheiden ist —,
wird zweimal gezeigt, einmal lesbar und einmal maskiert, denn nur diese Form
unterscheidet die beiden:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Dieselbe Unterscheidung gilt, wenn ein durchgehend griechisch oder kyrillisch
geschriebener Name mit einem ASCII-Namen der Quelle kollidiert, einschließlich
des einbuchstabigen Falls lateinisches `a` / kyrillisches `а`.

Wenn dir einer dieser Fälle begegnet und die Lösung nicht offensichtlich ist,
ist der sichere Weg, den selbst getippten Platzhalter zu löschen und den aus
dem `msgid` zu kopieren.

## Was die Prüfungen nicht leisten können { #what-the-checks-cannot-do }

Die Werkzeuge stellen sicher, dass deine Platzhalter unversehrt sind. Sie
können nicht beurteilen, ob die Übersetzung zutreffend, natürlich oder für den
Kontext richtig ist — das bleibt vollständig bei dir.

Zwei Dinge helfen mehr als jede Prüfung:

- **Lies den Hinweis für Übersetzende.** Eine Zeile, die mit `#.` beginnt und
  über der Nachricht steht, ist die entwickelnde Person, die dir sagt, wo die
  Nachricht auftaucht und was sie bedeutet.
- **Frag nach `msgctxt`.** Wenn dasselbe Wort zweimal mit unterschiedlichen
  Kontexten auftaucht, dann deshalb, weil die beiden unterschiedlich übersetzt
  werden müssen — „Open“ als Schaltfläche und „Open“ als Zustand etwa.
