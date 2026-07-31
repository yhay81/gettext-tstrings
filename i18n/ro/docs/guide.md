---
description: "API-ul de rulare: ce punct de intrare să folosești, legarea unui catalog, limbi per cerere, șiruri amânate, valori conștiente de locale și felul în care este raportată o traducere stricată."
---

# Ghid

Pagina de față este referința de rulare: tot ce face *codul aplicației tale* cu
această bibliotecă odată ce cataloagele există. Dacă nu ai văzut încă bucla
completă — marchează, extrage, tradu, compilează, rulează —
[tutorialul](tutorial.md) o parcurge o dată în cinci minute; crearea și
validarea cataloagelor sunt acoperite în [Extragere](extraction.md), iar felul
în care o echipă ține bucla în mișcare — cicluri de actualizare, CI, platforme
de traducere — este [În producție](workflow.md).

## Ce punct de intrare ar trebui să folosesc? { #which-entry-point-should-i-use }

Pachetul exportă mai multe feluri de a traduce un mesaj pentru că aplicațiile
leagă o limbă în mai multe feluri diferite. Alege după cum decide programul tău
în ce limbă se află:

| Situația ta | Folosește |
| --- | --- |
| O singură limbă pentru tot procesul — un CLI, o aplicație desktop, un script | `Translator`, apelat ca `_` |
| Câte o limbă pe cerere sau pe sarcină async — o aplicație web | `use_translations()` în jurul lucrului, apoi `tr()` |
| Un mesaj definit la momentul importului — o etichetă de formular, un enum, o constantă | `lazy_gettext()` sau `lazy_pgettext()` |
| Un număr decide formularea | `ngettext()` / `npgettext()`, în oricare dintre formele de mai sus |
| Randarea unui tipar fără niciun catalog implicat | `compile_template()` |

Tot ce urmează este acestea cinci, în această ordine.

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
    name = request.user.display_name
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

## Mai multe limbi deodată { #several-languages-at-once }

O singură cerere are adesea nevoie de mai multe limbi: o pagină randată pentru
cititor care pune la coadă și o notificare către un cont setat pe alta, sau un
rezumat care citează fiecare participant în limba lui. Legările se imbrichează,
iar ieșirea din blocul interior o restaurează pe cea din exterior.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Pe o listă de destinatari, șirurile amânate fac treaba: mesajul este scris o
singură dată, la import, și se randează o dată pentru fiecare limbă.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Legarea este o `ContextVar`, nu o stivă ținută pe un obiect partajat, așa că
cererile care se suprapun nu pot prelua limba una de la alta — inclusiv în
cazul în care *ies* din blocurile lor în ordinea în care au intrat, adică exact
întrepătrunderea pe care o stivă o greșește. Încărcarea unui catalog pentru
fiecare limbă este ieftină: `gettext.translation()` parsează fiecare `.mo` o
singură dată și dă mai departe copii care împart catalogul parsat.

!!! warning "Dacă un thread de lucru moștenește legarea depinde de build"

    Un `threading.Thread` gol sau `ThreadPoolExecutor.submit` pornește fie de la
    o copie a contextului apelantului, fie de la unul gol, iar care dintre ele
    este `sys.flags.thread_inherit_context` — adevărat implicit pe build-urile
    free-threaded, fals peste tot altundeva. Prin urmare, același cod randează
    limba legată pe 3.14t și catalogul global al procesului pe 3.14. Transmite
    contextul, în loc să depinzi de valoarea implicită:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` face deja asta pentru tine.

## Valori conștiente de locale { #locale-aware-values }

Această bibliotecă decide *unde* apare o valoare într-un mesaj tradus. Ea nu
localizează valoarea însăși. `{amount:,.2f}` este o specificație de format
Python cu comportament fix — o virgulă la fiecare trei cifre și un punct
înaintea zecimalelor — și produce aceleași caractere indiferent de limba
mesajului:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Germana scrie acel număr `1.234,50`, franceza `1 234,50`, iar hindi grupează
`1234567` ca `12,34,567`, nu ca `1,234,567`. Numerele, monedele, datele, orele
și unitățile țin de [Babel][babel-numbers]. Formatează întâi valoarea, apoi
așază șirul gata făcut:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Pentru un mesaj cu numărare, numărul face două treburi — selectează forma de
plural și apare în text — iar numai a doua este localizată. Păstrează numărul
brut pentru selecție și transmite șirul formatat pentru afișare:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatarea dinaintea apelului este și ceea ce ține o specificație de format în
afara catalogului: ce vede un traducător este o bucată de text gata făcută, nu
un număr plus instrucțiuni de randare a lui.

## Ce se întâmplă când un catalog este greșit { #what-happens-when-a-catalog-is-wrong }

Dacă substituenții unei traduceri nu se potrivesc cu sursa — un câmp lipsă,
necunoscut sau reformatat, care a scăpat de validare, venind dintr-un MO editat
manual, dintr-un catalog de la un furnizor sau dintr-o conductă care sare peste
verificator — comportamentul implicit este de a randa mesajul sursă în loc de
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

Aceste mesaje sunt scrise pentru cine poate acționa pe baza lor, iar în cazul
unei probleme de catalog acela este mai des un traducător decât un programator —
așa că acolo unde un substituent pare prezent, dar nu este, mesajul explică de
ce, în loc să repete că lipsește. Acolade cu lățime întreagă, un `{{name}}`
dublat, un spațiu neîntreruptor invizibil, o literă chirilică printre cele
latine: fiecare are formularea lui, listată cu exemple pe
[Pentru traducători](translators.md#reading-a-failure-message). Acea pagină este
scrisă ca să fie dată în mână persoanei care editează `.po`-ul.

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
