---
description: "Die t-string-zu-msgid-Konvention als versionierter Vertrag mit maschinenlesbarer Konformitätssuite."
---

# Spezifikation

Diese Bibliothek lässt sich nutzen, ohne diese Seite zu lesen — das
[Tutorial](tutorial.md) und die [Anleitung](guide.md) decken den Alltag ab.
Diese Seite richtet sich an Werkzeugautoren: Der Vertrag ist bewusst klein und
stabil, damit eine andere Implementierung — ein Extraktor, eine IDE, ein
Typprüfer oder ein zukünftiges `pygettext` — ihn umsetzen und interoperieren
kann.

[Spezifikation v1 lesen :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Regeln im Überblick

Ein **msgid** entsteht aus den Literalteilen in Quellreihenfolge und je einem
Token `{name}` pro Interpolation. Literale Klammern werden maskiert (`{` wird
`{{`). Namen müssen `str.isidentifier()` erfüllen und dürfen keine
Python-Schlüsselwörter sein. Konvertierungen und Formatspezifikationen bleiben
in der Anwendung.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *abgelehnt — kein einfacher Name* |

Eine **Übersetzung** ist gültig, wenn sie nur nackte `{name}`-Platzhalter
enthält, jeden erforderlichen Namen enthält und keinen unbekannten Namen
hinzufügt. Umstellen und Wiederholen sind erlaubt.

Bei Pluralformen ist die erlaubte Menge die Vereinigung und die erforderliche
Menge die Schnittmenge der Namen beider Zweige. So erlauben `t"One file"` und
`t"{n} files"` den Namen `n` in jeder Form, ohne ihn dort zu erzwingen.

Ein **leerer msgid** wird nie gesucht, weil gettext ihn für Metadaten reserviert.

## Konformität { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
beschreibt dieselben Regeln als maschinenlesbare Fälle. Eine Implementierung ist
zur Spec v1 konform, wenn sie alle Fälle reproduziert. Fehlermeldungen und
Exception-Typen sind nicht Teil dieser Prüfung.

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Die Referenzimplementierung führt diese Suite in ihren Tests aus.

## Versionierung

Eine inkompatible Änderung der msgid-Ableitung oder Validierung erhält eine
neue Version und `conformance/vN.json`. Rein additive Klarstellungen ändern die
Version nicht.
