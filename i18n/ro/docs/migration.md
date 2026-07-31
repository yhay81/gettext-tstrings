---
description: "Adoptarea t-stringurilor într-un proiect care are deja cataloage gettext: ce rămâne neatins, ce devine fuzzy și cum se mută câte un loc de apel pe rând."
---

# Migrare

Dacă proiectul tău folosește deja gettext, întrebările care decid dacă această
bibliotecă este adoptabilă sunt înguste: invalidează ea cataloagele pe care le
ai, poate coexista cu codul pe care nu ești gata să îl schimbi și cât din
mutare trebuie să se întâmple deodată. Răspunsurile, cele mai scurte primele:

| Întrebare | Răspuns |
| --- | --- |
| Fișierele `.po` și `.mo` existente funcționează în continuare? | Da. Aceleași fișiere, aceleași unelte. |
| Pot trăi apelurile vechi și cele noi în același fișier? | Da, iar o singură mapare de extractor le acoperă pe amândouă. |
| Se schimbă msgid-ul? | Nu, venind de la `.format()`. Da, venind de la `%`-format. |
| Trebuie să se mute tot proiectul deodată? | Nu. Un singur loc de apel este o schimbare validă. |
| Dar Jinja, șabloanele Django, JavaScript? | Neatinse, aceleași cataloage. |

Restul acestei pagini este detaliul din spatele fiecăruia dintre ele.

## De la `.format()`: msgid-ul nu se schimbă { #from-format-the-msgid-does-not-change }

Acesta este cazul în care migrarea nu costă mai nimic. Un mesaj `str.format` și
un mesaj t-string derivă *aceeași* cheie de catalog, pentru că cheia este
textul cu `{name}` lăsat în el, în ambele feluri:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Așa că traducerea existentă rămâne atașată. Pornind de la un catalog care ține

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

schimbă apelul, extrage din nou și actualizează:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Intrarea care se întoarce diferă prin două linii de metadate și prin nimic
altceva — un comentariu-marcaj care o identifică drept mesaj t-string și un
număr de linie din sursă:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Niciun flag `fuzzy`, nicio retraducere, în nicio limbă. Mesajul se randează
imediat:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` va raporta cataloagele ca fiind neactualizate"

    Acel comentariu-marcaj și numerele de linie mutate sunt de ajuns pentru ca
    `pybabel update --check` să spună că un catalog trebuie regenerat, pentru
    că el compară toată intrarea, nu doar traducerea. Rulează adevăratul
    `pybabel update` în același commit cu schimbarea de cod și comite
    cataloagele odată cu ea — același obicei pe care îl cere deja
    [poarta de CI](workflow.md#what-ci-gates).

## De la `%`-format: msgid-ul se schimbă, deci traducerile devin fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Sintaxa printf trăiește *înăuntrul* mesajului, așa că înlocuirea ei rescrie
cheia de catalog. Nu există cale de ocolire, iar acesta este costul cinstit al
renunțării la `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` recunoaște noul mesaj drept rudă apropiată a celui eliminat și
duce vechea traducere mai departe, marcată fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Trei lucruri de știut despre acea stare:

- **Nimic nu se strică la rulare.** Intrările fuzzy sunt excluse din `.mo`-ul
  compilat, așa că aplicația randează mesajul sursă până când un om confirmă
  perechea — [aceeași degradare](workflow.md#the-cycle-after-the-first-translation)
  prin care trece orice mesaj reformulat.
- **CI-ul rămâne verde cât timp ele sunt fuzzy.** Verificatorul de substituenți
  sare peste intrările fuzzy, exact cum face și `msgfmt --check-format`, pentru
  că o intrare care nu poate ajunge la rulare nu ar trebui să pice un build. În
  clipa în care un traducător șterge flagul, intrarea este verificată ca
  oricare alta — așa că un `%(name)s` rămas într-o traducere confirmată este
  prins atunci, adică exact în momentul în care altfel ar începe să se randeze.
- **Vechiul flag `python-format` călătorește odată cu ea** și ar trebui șters
  împreună cu flagul `fuzzy`, altfel `msgfmt --check-format` va continua să
  aplice reguli printf unui mesaj în format cu acolade.

Pentru substituenții printf denumiți, modificarea este mecanică — `%(name)s`
devine `{name}` și nimic altceva nu se mișcă — așa că un catalog mare înseamnă
o trecere scriptată urmată de recenzia unui traducător, nu o retraducere. `%s`
pozițional nu este mecanic: nu are niciun nume de purtat mai departe, iar
alegerea unuia este chiar scopul schimbării.

Prin urmare, migrarea poate înainta în ritmul pe care îl permite recenzia: o
intrare fuzzy neconvertită este o bucată de muncă vizibilă în catalog, nu un
build stricat.

## Apelurile vechi și cele noi coexistă { #old-and-new-calls-coexist }

Extractorul care citește t-stringuri citește și apelurile gettext obișnuite,
așa că o singură mapare acoperă un fișier aflat în plină migrare:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Ambele mesaje aterizează în același șablon, iar numai cel t-string poartă
comentariul-marcaj care activează verificarea suplimentară a acestei
biblioteci:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

El recunoaște `_()`, cele patru nume gettext standard, aliasurile `tr()` /
`ntr()` și `lazy_gettext()` / `lazy_pgettext()` amânate. Un ajutor propriu
trebuie [numit în mapare](extraction.md#registering-your-own-function-names).

La rulare, cele două stiluri sunt la fel de independente:
`gettext.translation()` întoarce un singur obiect translations, iar atât `_`,
cât și punctele de intrare ale acestei biblioteci citesc din el.

## Ce nu se mută { #what-does-not-move }

- **Limbajele de șabloane.** `{% trans %}` din Jinja2, etichetele de șablon
  Django și extractoarele lor Babel funcționează neschimbate în continuare și
  alimentează în continuare aceleași cataloage PO. T-stringurile sunt sintaxă
  Python; ele se aplică sursei Python.
- **Fișierele tale de catalog.** Nicio schimbare de format, niciun fișier nou,
  niciun pas de conversie.
- **Platforma ta de traducere.** Schimbul de `.po` este identic, iar flagul
  `python-brace-format` pe care îl poartă un mesaj t-string este același flag
  pe care îl poartă un mesaj `.format()` — așa că QA-ul de substituenți
  funcționează în continuare.
- **Codul care nu e Python.** Un catalog JavaScript sau C din același proiect
  rămâne neafectat.

## O listă de verificare pentru migrare { #a-migration-checklist }

1. Adaugă extra-ul `babel` acolo unde rulează `pybabel` și schimbă maparea
   `python` din `babel.cfg` la metoda `gettext_tstrings` — o singură mapare
   acoperă atunci ambele stiluri, iar `-k` funcționează în continuare pentru
   apelurile obișnuite.
2. Convertește întâi locurile de apel `.format()`. Extrage din nou, rulează
   `pybabel update` și comite cataloagele odată cu codul; nu te aștepta la
   nicio intrare fuzzy.
3. Convertește locurile de apel `%`-format în loturi pe care le poți da la
   recenzie, rescriind substituenții purtați mai departe și ștergând flagurile
   `fuzzy` și `python-format`.
4. Repară ce respinge restricția: o interpolare trebuie să fie un nume simplu,
   deci `t"Hello {user.name}"` devine întâi o variabilă locală. Aceasta este o
   modificare la locul de apel, nu una de catalog.
5. Activează `strict = true` în maparea extractorului odată ce trecerea s-a
   încheiat, astfel încât un mesaj care nu poate fi extras să pice
   [buildul](extraction.md#lenient-locally-strict-in-ci) în loc să dispară din
   șablon.
6. Adaugă verificarea de la rulare din [În producție](workflow.md#what-ci-gates):
   randează câte un mesaj pentru fiecare limbă livrată printr-un `Translator`
   strict.

Pașii 2 și 3 sunt commituri obișnuite. Nimic din această listă nu are nevoie de
o zi de comutare.
