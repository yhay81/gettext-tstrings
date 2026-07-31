---
description: "Was das Übersetzen einer kleinen Website in fünfunddreißig Sprachen tatsächlich zerbricht, welche dieser Fälle die Bibliothek für dich abfangen kann und welche nicht."
---

# Fallstricke

Diese Website ist in fünfunddreißig Sprachen übersetzt, und jede dieser
Ausgaben entstand, indem genau die Schleife gedreht wurde, die diese
Dokumentation lehrt. Nach Branchenmaßstäben ist das ein kleines Korpus — und
es genügte trotzdem, um in die meisten Fallen zu tappen, die i18n schwerer
machen, als es aussieht.

Jeder Abschnitt unten ist etwas, das hier tatsächlich schiefging: wie es sich
damals darstellte und wo die Grenze verläuft zwischen dem, was die Bibliothek
für dich prüft, und dem, was deinem Urteil überlassen bleibt.

## Eine Variable umzubenennen übersetzt einen Satz neu { #renaming-a-variable-retranslates-a-sentence }

Die msgid ist der Katalogschlüssel, und ein interpolierter Name steht *darin*.
Eine Konstante auf Modulebene zu heben und sie so groß zu schreiben, wie es
der Python-Stil verlangt — `author` zu `AUTHOR` —, machte aus
`Copyright © 2026 {author} · MIT License` eine Nachricht, die kein Katalog je
gesehen hatte. Jede Übersetzung dieser Zeile wäre erneut durch den
fuzzy-Zyklus gegangen, in jeder Sprache, für eine Umbenennung, die nichts
änderte, was ein Leser sehen konnte.

Die Bibliothek hält dich nicht auf: Beide Schreibweisen sind gültige
Platzhalternamen. Was sie tut, ist, den Namen schützenswert zu *machen* — eine
Interpolation muss ein [einfacher Name](internals.md#from-template-to-msgid)
sein, also steht im Katalogschlüssel ein Wort, das eine übersetzende Person
lesen kann, und kein Ausdruck.

Der Spiegelfall ist konstruktionsbedingt sicher. Konvertierungen und
Formatspezifikationen sind nicht Teil der msgid, deshalb ändert die
Verschärfung von `{amount:,.2f}` zu `{amount:,.0f}` keinen Schlüssel und
entwertet nirgends eine Übersetzung.

## `nplurals=2` bedeutet nicht zwei verschiedene Strings { #nplurals-2-does-not-mean-two-different-strings }

Türkisch, Ungarisch, Persisch und Bengalisch deklarieren alle zwei
Pluralformen, und in allen vieren sind die beiden Formen einer gezählten
Nachricht berechtigterweise *derselbe String* — das Substantiv bleibt nach
einem Zahlwort im Singular, also ist `{n} sayfa` für eine Seite ebenso richtig
wie für zehn. Wer die Dopplung „korrigiert“, zerstört die Übersetzung.

Der umgekehrte Fehler ist ebenso leicht. Die dritte Form des Lettischen gilt
**allein der Null**; die zweite des Slowenischen ist ein **Dual**, für genau
zwei; die letzte Form des Rumänischen verlangt das Wort `de`, das den ersten
beiden fehlen muss. Diese Plätze mit einem Singular und einem Plural zu
füllen, ergibt einen Katalog, der nur bei Zählwerten falsch ist, die niemand
testet.

Schlimmer noch: Die *Reihenfolge* der Plätze ist nicht semantisch. Walisisch
indiziert seine fünf Formen so, dass `msgstr[0]` der allgemeine Fall ist und
`msgstr[1]` der Singular. Füllt man sie in der naheliegenden Reihenfolge,
landet der Singular dort, wo ihn jede ungezählte Nachricht findet.

Die Bibliothek nimmt sich nichts davon an, und das ist der Punkt: Die
Pluralregel der Zielsprache steht im Kopf ihres eigenen Katalogs, und die
[Vereinigungs-/Schnittmengenregel](spec.md) erlaubt einer Übersetzung mehr
Formen als der Quelle oder weniger. Was sie prüft, ist das Einzige, was sich
ohne Kenntnis der Sprache prüfen lässt — dass jede Form die Platzhalter
behält, die sie braucht.

## Zwei Formen können aus gutem Grund identisch sein { #two-forms-can-be-identical-for-a-reason }

Irisch hat fünf Pluralformen, und im Build-Bericht dieser Website sind mehrere
davon gleich geschrieben. Das ist kein Copy-Paste-Versehen: *leathanach*
beginnt mit `l`, und keine der beiden Anlautmutationen, die irische Zahlwörter
auslösen, wird auf `l` geschrieben. Die Formen leisten trotzdem echte Arbeit —
der Stamm wechselt zwischen *leathanach* und *leathanaigh*, und Zählwerte über
zehn kehren zum Singular zurück —, doch kein Substantiv mit der Bedeutung
„Seite“ würde den Unterschied zeigen.

Jede Prüfung, die doppelte Formen als verdächtig meldet, meldet korrektes
Irisch. Hier kann nur ein Mensch prüfen, der die Sprache beherrscht.

## Eine Nachricht kann nur mit einer Zahl kongruieren { #a-message-can-only-agree-with-one-count }

Der Build-Bericht dieser Website nennt, wie viele Seiten gerendert wurden und
wie lange es dauerte. Ihn als „Rendered {n} pages in {seconds} seconds“ zu
schreiben, sieht harmlos aus und ist nicht übersetzbar: gettext wählt eine
Form anhand einer Zahl, und diese Zahl ist `n`. Das Wort *seconds* müsste mit
einer Zahl kongruieren, welche die Pluralmaschinerie nie zu sehen bekommt.

Die Lösung ist, die zweite Größe als Einheitenzeichen statt als Wort zu
schreiben — und Einheitenzeichen sind selbst lokalisiert: Die Kataloge dieser
Website führen `s`, `с`, `ث`, `שנ׳` und `mp`, und die französische, spanische
und schwedische Typografie verlangt vor dem Zeichen ein Leerzeichen, wo das
Englische keines setzt. Nichts davon ist Sache der Bibliothek — wohl aber zu
bemerken, dass eine Nachricht *zwei* Kongruenzen bräuchte, und das einzige
Werkzeug dafür ist, die Nachricht anders zu formulieren.

## Einen englischen Satz zu bearbeiten bearbeitet fremde Grammatik { #editing-an-english-sentence-edits-foreign-grammar }

Auf der Startseite stand einmal „all ten language editions“. Die Zahl zu
streichen — eine englische Änderung von einem Wort, vorgenommen, weil die Zahl
immer wieder veraltete — machte aus einem pluralischen Subjekt ein
singularisches. Spanisch, Italienisch, Portugiesisch, Russisch, Ukrainisch,
Griechisch, Niederländisch und Hebräisch mussten das Verb allesamt neu
kongruieren; in mehreren musste auch das Partizip geändert werden.

Eine Quelländerung, die sich auf Englisch trivial liest, ist es stromabwärts
nicht. Sie als fuzzy zu markieren — genau das tut `pybabel update` — ist der
Mechanismus, der jeder übersetzenden Person die Gelegenheit gibt, es zu
bemerken.

## Unsichtbare Unterschiede überstehen jedes Copy-Paste { #invisible-differences-survive-every-copy-paste }

Der Leitfaden zitiert eine Diagnosemeldung, die `(nаme)` enthält — eine
bewusste Escape-Schreibweise, denn das benannte Zeichen ist ein kyrillisches
`а`, das kein Leser vom lateinischen unterscheiden kann. Übersetzende dieser
Website haben diese Escape-Schreibweise **fünfmal einzeln** in das
tatsächliche Zeichen umgewandelt, in fünf verschiedenen Sprachen, und dabei
jedes Mal eine Seite erzeugt, die richtig aussah und falsch war.

Diesen Fall fängt die Bibliothek tatsächlich ab, und er ist der Grund, warum
die Diagnostik so geformt ist, wie sie ist: Ein Platzhalter, dessen Buchstaben
Schriftsysteme mischen, wird
[zweimal gemeldet](internals.md#diagnostics-are-part-of-the-design), einmal
lesbar und einmal escaped, weil nur die escapete Schreibweise die beiden
unterscheidet. Ein geschütztes Leerzeichen innerhalb von geschweiften Klammern
wird aus demselben Grund als Codepoint ausgegeben. Der Katalogprüfer weist die
Nachricht zurück, bevor sie ausgeliefert werden kann.

## Nicht leer heißt nicht übersetzt { #non-empty-is-not-translated }

Ein Katalog, der mit den in die msgstrs kopierten msgids aufgesetzt wurde,
besteht jede naive Prüfung: Nichts ist leer, nichts ist fuzzy, die
Nachrichtenmenge stimmt exakt überein. Eine Sprachausgabe dieser Website ging
so für mehrere Stunden live. Ebenso acht Seiten einer anderen Ausgabe, die
byte-identische Kopien der englischen Quelle waren — was eine Prüfung besteht,
die Codeblöcke zwischen beiden vergleicht, denn es ist dieselbe Datei.

Beides kann eine Übersetzungsbibliothek nicht sehen. Beides ist billig zu
testen, sobald man weiß, dass man es muss: gegen die Quelle vergleichen und
einen Unterschied verlangen.

## Der Katalog ist nicht das Einzige, was übersetzt wird { #the-catalog-is-not-the-only-translated-thing }

Zwei Fehlschläge hier hatten nichts mit gettext zu tun.

Eine Überschrift zu übersetzen ändert den daraus erzeugten Anker, sodass jeder
seitenübergreifende Link in diesen Abschnitt bricht — lautlos und nur in
dieser Sprache. Diese Website heftet an jede Überschrift den englischen Anker,
und ein Test leitet die erwartete Liste von der englischen Seite ab.

Und der Website-Generator liefert Oberflächenübersetzungen für
achtundsechzig Sprachen mit, worunter weder Suaheli noch Irisch fällt. Fehlt
eine, fällt der Build nicht auf Englisch zurück; das Template-Include schlägt
fehl und die Sprachausgabe lässt sich überhaupt nicht bauen. Zwei eigene
Dateien dieses Repositorys existieren, um diese Lücke zu füllen.

## Auch deine Werkzeuge haben Fehler { #your-tools-have-bugs-too }

Der CI-Schritt, den diese Dokumentation zum Aufspüren veralteter Kataloge
empfiehlt, `pybabel update --check`, kann diese Aufgabe für kein Projekt
erfüllen, das `pgettext` oder `npgettext` verwendet — er meldet jeden Katalog
mit einem `msgctxt` bei jedem Lauf als veraltet, wegen eines Fehlers darin,
wie der Vergleich Nachrichten nachschlägt. Er wurde hier beim Versuch, ihn zu
benutzen, gefunden, upstream gemeldet und ist
[vollständig samt Umgehung beschrieben](workflow.md#what-ci-gates).

Die allgemeine Lehre ist die unbequeme: Eine Schranke, die immer rot ist, ist
schlimmer als gar keine, weil ein Team sie abschaltet. Prüfe, dass deine
CI-Prüfung tatsächlich bestehen kann, bevor du ihr zutraust, fehlzuschlagen.

## Wofür die Bibliothek da ist, in einer Zeile { #what-the-library-is-for-in-one-line }

Das meiste auf dieser Seite ist Urteilsvermögen, das kein Werkzeug übernehmen
kann. Was ein Werkzeug *kann*, ist zu garantieren, dass eine Übersetzung die
Struktur des Satzes, den sie übersetzt, nicht verändern kann — keinen Wert
weglassen, keinen erfinden, keinen umformatieren und nicht in deine Objekte
greifen — und das in einem Satz zu sagen, mit dem die Person, die es beheben
muss, etwas anfangen kann. Das ist alles, was diese Bibliothek verspricht, und
der Rest dieser Website ist, wie sie es hält.
