---
description: "Dreißig Jahre gettext, zwei PEPs im Abstand von zehn Jahren und die stdlib-Diskussion, die als „not planned“ geschlossen wurde: warum diese Bibliothek existiert, mit Links zu den Quellen."
---

# Hintergrund

Diese Bibliothek liegt am Schnittpunkt zweier langer Geschichten — die eine
darüber, wie Software übersetzt wird, die andere darüber, wie Python Strings
interpoliert —, die sich 2025 endlich kreuzten und dann genau an dem Punkt
ins Stocken gerieten, an dem eine kleine, sorgfältige Konvention gebraucht
wurde. Diese Seite erzählt beide Geschichten, mit Links zu den Quellen, denn
die Designentscheidungen auf dieser Website lassen sich leichter beurteilen,
wenn man die Fragen sieht, die sie beantworten.

## Das gettext-Ökosystem { #the-gettext-ecosystem }

[GNU gettext] ist seit Mitte der 1990er-Jahre der Weg, auf dem freie Software
übersetzt wird: Strings im Code markieren, in eine Vorlage extrahieren, den
Übersetzenden eine Katalogdatei pro Sprache geben, kompilieren, zur Laufzeit
laden. Um diese Schleife herum wuchs ein ganzes Ökosystem — PO-Editoren,
Review-Workflows und Übersetzungsplattformen, die alle dasselbe Dateiformat
sprechen — und Python liefert seit mehr als zwei Jahrzehnten ein
[`gettext`-Modul][stdlib-gettext] in seiner Standardbibliothek mit. Die
Laufzeithälfte der Übersetzung war nie das Problem.

Ungeklärt war stets die andere Hälfte: *wie der Katalogstring aussieht*. Eine
`%(name)s`-Nachricht gibt Übersetzenden printf-Syntax in die Hand, bei der
ein einziger gelöschter Buchstabe zum Produktionsabsturz wird; eine
`.format()`-Nachricht gibt dem Katalog Attributzugriff auf lebende Objekte.
([Warum t-strings](comparison.md) führt beides vor, mit den Fehlschlägen zur
Ansicht.) Und f-strings — die Syntax, die der meiste Python-Code inzwischen
bevorzugt — können gar nicht erst teilnehmen: Wenn irgendeine Bibliothek
einen sieht, ist er bereits ein fertiger String. Versucht wird es trotzdem,
oft genug, dass Babels Issue-Tracker die Anläufe sammelt
([#594][babel-594], [#715][babel-715]); der Fehlschlag ist strukturell, kein
fehlendes Feature.

## Zwei PEPs, zehn Jahre auseinander { #two-peps-ten-years-apart }

2015 schrieben Alyssa Coghlan und Nick Humrich [PEP 501] und schlugen
Interpolationstemplates vor, deren erstgenannte Motivation i18n war —
„providing a cleaner syntax for i18n translation“, in den Worten des PEP
selbst. Der Vorschlag wurde zurückgestellt, unter anderem weil die Diskussion
zeigte, dass der i18n-Fall erhebliche zusätzliche Überlegungen mit sich
brachte, die einfachere Anwendungsfälle nicht hatten.

Ein Jahrzehnt später griff [PEP 750] — von Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou und Dave Peck — die Idee als
t-strings wieder auf, wurde [im April 2025 angenommen][sc-resolution] und
erschien im Oktober 2025 mit [Python 3.14]. PEP 501 wurde daraufhin zu seinen
Gunsten zurückgezogen. Ein Detail ist für diese Seite wichtig: i18n gehört
*nicht* zu den erklärten Motivationen von PEP 750. Das PEP verallgemeinerte
den Mechanismus — ein Template-Typ, den jede Bibliothek konsumieren kann —
und ließ die Übersetzungsfrage genau dort liegen, wo PEP 501 sie zehn Jahre
zuvor geparkt hatte: offen.

Mit Python 3.14 hatte die Sprache also genau die Datenstruktur, die ein
Nachrichtenkatalog braucht, und keine Konvention, sie als solchen zu
verwenden.

## Die stdlib-Diskussion { #the-stdlib-discussion }

Zwei Monate vor dem Erscheinen von 3.14 schlug Adrian Mönnich (ThiefMaster,
ein Maintainer des Indico-Projekts) vor, diese Lücke in der
Standardbibliothek selbst zu schließen: Der Thread
[Support t-strings in gettext][discuss-thread] auf discuss.python.org,
eröffnet im August 2025, kam mit einem funktionierenden
[Pull Request][cpython-pr], der t-string-Unterstützung sowohl zu `gettext`
als auch zu `pygettext` hinzufügte.

Der Thread lohnt die vollständige Lektüre, denn er bringt jede harte Frage an
die Oberfläche, die diese Bibliothek später beantworten musste:

- **Was darf eine Interpolation sein?** Nur ein einfacher Name, oder auch
  Attribute und Aufrufe mit einem abgeleiteten Platzhalternamen? Jede Antwort
  tauscht Bequemlichkeit gegen msgid-Stabilität und Katalogsicherheit.
- **Was verlangen Pluralformen,** wenn das Pluralsystem der Zielsprache von
  dem der Quellsprache abweicht?
- **Ist gettext überhaupt das richtige Ziel?** Barry Warsaw — der schon
  während der Entwicklung von PEP 750 argumentiert hatte, dass t-strings für
  i18n nicht gut geeignet seien — verwies auf sein [`flufl.i18n`][flufl-i18n]
  und dessen `$`-String-Stil als das freundlichere Werkzeug; andere
  plädierten dafür, gettext ganz hinter sich zu lassen, zugunsten neuerer
  Systeme wie [Fluent].
- **Und die Meta-Frage:** Was auch immer die Standardbibliothek ausliefert,
  kann sich im Grunde nie wieder ändern. Eine Konvention mit so vielen
  offenen Entscheidungen beim ersten Versuch einzufrieren ist riskant.

Ein Konsens bildete sich nicht. Das CPython-Issue wurde
[als „not planned“ geschlossen][cpython-issue], und der Pull Request wurde im
Oktober 2025 ungemergt geschlossen, Tage nach dem Release von 3.14. Die
Fähigkeit existierte in der Sprache; die Konvention hatte kein Zuhause.

## Warum zuerst ein Paket { #why-a-package-first }

Das ist die Lücke, die dieses Projekt von außerhalb der Standardbibliothek zu
füllen beschloss, auf eine bewusste Wette hin: Eine Konvention reift
schneller, wo sie frei versionieren und sich ihre Verbreitung Fall für Fall
verdienen kann, und die Standardbibliothek — die beim ersten Mal richtig
liegen muss — ist der Ort, an dem eine Konvention *ankommen* sollte, nicht
der, an dem sie ausgearbeitet wird.

Konkret hat jede umstrittene Frage aus dem Thread hier eine niedergeschriebene
Antwort, jede auf ihrer eigenen Seite:

- Interpolationen sind **ausschließlich einfache Namen**, damit msgids stabil
  und aussagekräftig bleiben — [die Anleitung](guide.md#safety-and-scope)
  zeigt die Regel, [Funktionsweise](internals.md#from-template-to-msgid) die
  Gründe.
- **Formatierung bleibt vollständig aus dem Katalog heraus**
  ([Warum t-strings](comparison.md)).
- **Pluralformen** folgen einer Vereinigungs-/Schnittmengenregel, die es dem
  Pluralsystem einer Zielsprache erlaubt, vom System der Quellsprache
  abzuweichen ([Spezifikation §4](spec.md)).
- Ein fehlerhafter Katalog **fällt zurück, statt abzustürzen**, und wahrt
  damit gettexts eigenen Vertrag
  ([die Anleitung](guide.md#what-happens-when-a-catalog-is-wrong)).
- Und die gesamte Konvention ist eine
  [versionierte Spezifikation](spec.md) mit einer maschinenlesbaren
  Konformitätssuite — so geschrieben, dass eine andere Implementierung,
  einschließlich einer künftigen in der Standardbibliothek, sie unverändert
  übernehmen und interoperieren könnte.

Die Diskussion ist nicht beendet, und dieses Projekt ist ein Teilnehmer an
ihr, kein Urteil über sie. Wer Produktionserfahrung mit gettext hat, die
diese Entscheidungen berührt, findet im [selben Thread][discuss-thread] und
in den [Discussions][gh-discussions] dieses Repositorys den Ort, an dem
die Diskussion weitergeht.

## Zeitleiste { #timeline }

| Wann | Was geschah |
| --- | --- |
| Mitte der 1990er | GNU gettext etabliert den PO/POT/MO-Workflow, den Übersetzende und Plattformen bis heute sprechen. |
| 2015 | [PEP 501] schlägt Interpolationstemplates vor, mit i18n als erster Motivation; zurückgestellt. |
| 2016 | f-strings erscheinen in Python 3.6 — die Interpolation bekommt ihre Syntax, und die Übersetzung kann sie nicht nutzen. |
| Jul 2024 | [PEP 750] schlägt t-strings vor. |
| Apr 2025 | PEP 750 wird [angenommen][sc-resolution]; PEP 501 zu seinen Gunsten zurückgezogen. |
| Aug 2025 | Der Thread [Support t-strings in gettext][discuss-thread] öffnet, mit einem [Pull Request][cpython-pr] für die stdlib. |
| Okt 2025 | [Python 3.14] erscheint mit t-strings; das stdlib-Issue wird als [not planned][cpython-issue] geschlossen. |
| 2026 | `gettext-tstrings` erscheint als Alpha, mit [Spezifikation v1](spec.md) und ihrer Konformitätssuite. |

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
