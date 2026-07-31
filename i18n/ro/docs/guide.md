---
description: "API-ul de rulare: legarea unui catalog, limbi per cerere, șiruri amânate și felul în care este raportată o traducere stricată."
---

# Ghid

Pagina de față este referința de rulare: tot ce face *codul aplicației tale* cu
această bibliotecă odată ce cataloagele există. Dacă nu ai văzut încă bucla
completă — marchează, extrage, tradu, compilează, rulează —
[tutorialul](tutorial.md) o parcurge o dată în cinci minute; crearea și
validarea cataloagelor sunt acoperite în [Extragere](extraction.md), iar felul
în care o echipă ține bucla în mișcare — cicluri de actualizare, CI, platforme
de traducere — este [În producție](workflow.md).

## Legarea unui catalog { #binding-a-catalog }

Forma recomandată oglindește utilizarea pe clase a lui gettext: leagă o dată un
obiect de traducere standard și folosește procesorul apelabil ca `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Funcțiile de la nivelul modulului urmează numele bibliotecii standard și
convenția ei de apel strict pozițional:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` și `ntr` sunt aliasuri exacte pentru `gettext` și `ngettext`.

## Limba per cerere { #per-request-language }

Un framework web alege o limbă pentru fiecare cerere. Leagă traducerile cererii
de contextul curent și fiecare apel de la nivelul modulului se va rezolva în
acea limbă, în siguranță de-a lungul cererilor concurente:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` leagă fără un bloc `with`, pentru framework-uri
care își gestionează singure ciclul de viață al cererii;
`get_translations()` citește legarea curentă. Un argument `translations=`
explicit învinge întotdeauna contextul, iar un context nelegat revine la
funcțiile gettext instalate global de biblioteca standard. Exemple lucrate
pentru Flask și pentru middleware ASGI se află pe pagina
[În producție](workflow.md#binding-a-language-at-runtime).

## Traducerea amânată { #deferred-translation }

Un t-string își captează valorile nerăbdător, ceea ce este greșit pentru un șir
definit la momentul importului — o etichetă de formular, o valoare de enum, o
constantă de modul — care trebuie să se randeze în orice limbă este activă
atunci când el este *folosit*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Un `LazyString` se randează prin `str()`, `format()` și f-stringuri, și se
compară egal cu textul său randat.

!!! note "Nehashabil în mod intenționat"

    Textul unui `LazyString` depinde de limba activă, așa că un hash s-ar
    schimba la o comutare de limbă și ar corupe pe tăcute orice set sau dict
    care îl ține. Apelează întâi `str()` dacă ai nevoie de o cheie.

`strict` se hotărăște acolo unde este scris mesajul, nu acolo unde se randează:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Un șir amânat se randează oriunde ajunge să fie folosit în cele din urmă —
înăuntrul unui șablon, al unui formular, al unei linii de jurnal — iar locul
acela rareori știe dacă este vorba de o rulare de test sau de producție.
Trecerea lui `strict=True` la definire este ceea ce permite ca aceeași alegere
[zgomotos în CI, îngăduitor în producție](#what-happens-when-a-catalog-is-wrong)
să se aplice și unui șir care nu este randat la locul lui de apel.

Formele de plural depind de un număr cunoscut abia la rulare, așa că randează-le
nerăbdător cu `ngettext`, acolo unde numărul este cunoscut.

## Ce se întâmplă când un catalog este greșit { #what-happens-when-a-catalog-is-wrong }

Dacă substituenții unei traduceri nu se potrivesc cu sursa — un câmp lipsă,
necunoscut sau reformatat, care a scăpat de validare, venind dintr-un MO editat
manual, dintr-un catalog de la un furnizor sau dintr-o conductă care sare peste
verificator — comportamentul implicit este de a reproduce textul sursă în loc de
a ridica o excepție. Asta oglindește contractul propriu al lui gettext, potrivit
căruia un catalog prost nu strică niciodată aplicația.

Cu `Hello {name}` tradus ca `こんにちは {nombre}`, randarea reușește, iar un
singur avertisment ajunge la jurnalizatorul `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Avertismentul se declanșează o dată per mesaj și tipar, nu o dată per randare,
așa că o intrare stricată din catalog nu inundă un jurnal.

Optează pentru eșecul zgomotos în teste și în CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Aceeași căutare ridică atunci o excepție, purtând aceeași propoziție, fără
jumătatea „using source text”:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Citirea unui mesaj de eșec { #reading-a-failure-message }

Aceste mesaje sunt scrise pentru cine poate acționa pe baza lor, iar în cazul
unei probleme de catalog acela este mai des un traducător decât un programator.
A raporta doar că `{name}` lipsește este o fundătură atunci când cititorul vede
acele caractere chiar în fața lui, așa că acolo unde un substituent pare
prezent, dar nu este, mesajul spune de ce. Față de sursa `Hello {name}`, fiecare
dintre acestea este raportat sub
`translation does not match the source placeholders:`

| Ce spune traducerea | Motivul pe care îl dă |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` lipsește (acoladele din jurul lui nu sunt `{` și `}` din ASCII) |
| `こんにちは {{name}}` | `{name}` lipsește (este scris `{{name}}`, ceea ce este modul de a escapa o acoladă literală) |
| `こんにちは name` | `{name}` lipsește (numele apare, dar nu între acolade) |
| `こんにちは {名前}` | `{name}` lipsește; `{名前}` nu se află în mesajul sursă |

Caracterele care nu se pot vedea au parte de un tratament propriu. Un spațiu
neîntreruptor între acolade este ceva ce produce o metodă de introducere și nu
arată niciun editor, așa că mesajul îl tipărește după punctul de cod, în loc să
numească un caracter pe care cititorul nu îl poate găsi:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un nume ale cărui litere amestecă sisteme de scriere — cazul homoglifelor, în
care un `а` chirilic nu se deosebește de unul latin — este arătat de două ori, o
dată lizibil și o dată escapat, ceea ce este singura formă care le distinge una
de alta:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Aceeași dezambiguizare se aplică atunci când un nume grecesc sau chirilic scris
în întregime într-un singur alfabet intră în conflict cu un nume sursă ASCII,
inclusiv cazul cu o singură literă `a` latin / `а` chirilic.

## Randarea unui tipar fără catalog { #rendering-a-pattern-without-a-catalog }

`compile_template` expune același mecanism cu un nivel mai jos: transformă un
t-string în msgid-ul lui plus un set legat de valori, și randează orice tipar îi
dai.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validează după aceleași reguli și **ridică întotdeauna** o excepție la
nepotrivire. Nu există un mod permisiv aici: permisivitatea există pentru ca o
căutare în *catalog* să poată degrada la textul sursă, iar un tipar pe care l-ai
transmis chiar tu nu are de la ce să degradeze.

## Siguranță și domeniu de aplicare { #safety-and-scope }

Acesta este valid:

```python
tr(t"Hello {name}")
```

Acestea sunt respinse în mod intenționat:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Calculează întâi o valoare cu înțeles:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Restricția produce chei de catalog stabile, dă traducătorilor nume folositoare
și împiedică un șir tradus să devină un limbaj de expresii.

Garanția este limitată la *structură și formatare*: o traducere nu este
niciodată evaluată și nu poate adăuga niciodată acces la atribute, apeluri,
conversii sau specificații de format. Două lucruri rămân în responsabilitatea
apelantului, exact ca la gettext din biblioteca standard — **escaparea** ieșirii
randate pentru destinația ei (HTML, shell, terminal) și **integritatea
catalogului**, de vreme ce un catalog ostil poate repeta un substituent pentru a
amplifica dimensiunea ieșirii, ceea ce este inerent oricărui i18n bazat pe
substituenți.
