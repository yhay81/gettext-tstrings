---
description: "Același mesaj traductibil scris cu %-format, .format(), $-stringuri flufl.i18n și un t-string, inclusiv modul în care fiecare leagă valorile și tratează un catalog deteriorat."
---

# De ce t-stringuri

Patru moduri de a pune o valoare într-un mesaj traductibil, comparate pe
aceeași propoziție. Pe scurt:

- Cu **%-format**, o singură literă ștearsă de un traducător devine o cădere
  în producție.
- Cu **str.format**, o traducere poate citi atribute de pe obiectele pe care
  le transmite codul tău — inclusiv secrete.
- Cu **$-stringuri** (flufl.i18n), valorile sunt preluate implicit din
  variabilele funcției apelante, iar substituenții cu punct ajung și la atribute.
- Cu **t-stringuri**, formatarea rămâne în codul tău, traducerile sunt
  verificate la rulare, iar un catalog stricat revine la textul sursă în loc
  să cadă.

Restul paginii este dovada, metodă cu metodă.

!!! note "Trei părți ating fiecare mesaj tradus"

    Un **catalog** este fișierul cu traduceri — `.po` cât timp îl editează
    oamenii, compilat în `.mo` pentru a fi încărcat de aplicație
    ([tutorialul](tutorial.md) le parcurge pe amândouă). Trei părți ating
    fiecare mesaj: **dezvoltatorul** scrie șirul sursă, un **traducător**
    editează catalogul — adesea pe o platformă externă, departe de orice
    recenzie de cod — iar **aplicația** le randează împreună la rulare.
    Fiecare stil de formatare de mai jos răspunde diferit la aceeași
    întrebare: *cât din limbajul de format ajunge sub controlul catalogului?*
    În exemple, `_` este numele convențional al funcției de traducere, iar
    `tr` este cel al acestei biblioteci.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Ce poate merge prost: o singură literă ștearsă dintr-o traducere face
randarea să cadă.

Șirul din catalog poartă sintaxă printf, inclusiv o literă de tip la final —
`s`-ul din `%(name)s` — ușor de trecut cu vederea și ușor de stricat:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

O modificare de un caracter într-un editor PO devine un traceback în
producție. GNU `msgfmt --check-format` chiar o prinde, dar numai pentru
mesajele marcate `python-format` și numai dacă în drumul său către aplicație
catalogul trece într-adevăr prin msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Elimină litera de tip de la final, păstrând totodată un substituent cu nume,
liber reordonabil. Ce poate merge prost se mută pe cealaltă parte a schimbului:
traducerea capătă putere asupra obiectelor tale.

`str.format` este un mic limbaj de expresii, iar a-l apela pe un șir înseamnă
a-i da acelui șir dreptul să îl folosească:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Acum înlocuiește acele șiruri literale cu orice returnează `_()`. Dacă o
traducere a lui `Hello {name}` se întoarce ca `{conf.api_key}`, randarea ei îți
tipărește cheia de API — catalogul, nu codul tău, a decis ce anume s-a citit. Un
catalog nu este cod, dar călătorește ca datele: afară către o platformă de
traducere, prin mai multe mâini, înapoi ca `.po`, compilat într-un `.mo`, uneori
adus din afara proiectului tău cu totul. `.format()` dă fiecărui pas al acelei
călătorii acces la atributele obiectelor pe care le transmiți.

## `$`-stringuri și flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] din biblioteca standard furnizează
limbajul de interpolare `$name`, dar nu este el însuși un API de traducere.
[`flufl.i18n`][flufl-i18n] combină acel stil cu căutarea în cataloage gettext.
Observă că valoarea nu este niciodată transmisă: flufl.i18n construiește spațiul
de nume al substituțiilor din globalele și localele apelantului — orice variabile
există la punctul de apel sunt disponibile mesajului. O mapare `extras`
opțională are întâietate față de amândouă. Sintaxa lui văzută de traducător nu
are literă de tip la final și nici specificator de format, iar substituenții
rămân liber reordonabili.

O substituție indisponibilă nu ridică o excepție. Cu `name = "Ada"` și fără
niciun `nombre` în spațiul de nume al apelantului, o traducere din catalog a lui
`Hello $nombre` se randează ca `Hello $nombre`: substituentul nerezolvat rămâne
vizibil. Acel [comportament documentat][documented behavior] păstrează restul mesajului tradus în loc
să facă apelul să eșueze. Excepțiile ridicate în timpul rezolvării unui atribut
sau al conversiei unei valori se pot propaga totuși.

`flufl.i18n` este mai capabil decât un `string.Template` gol într-un fel
relevant. [Template-ul lui propriu][custom Template] acceptă substituenți cu
punct, precum `$settings.api_key`, iar [translator][translator]-ul lui rezolvă acele căi față de valorile
apelantului. Un substituent tradus poate numi orice locală sau globală
disponibilă a apelantului și, cu sintaxa cu punct, îi poate parcurge atributele.
Asta este comod atunci când un mesaj are nevoie de un atribut, dar face
totodată cadrul apelantului parte din spațiul de nume al substituțiilor
catalogului. Comparația de mai jos descrie `flufl.i18n` 6.0.0, nu orice
utilizare posibilă a lui `string.Template`.

El răspunde totodată la o întrebare pe care celelalte două stiluri de formatare
o lasă în întregime aplicației: *care* limbă este cea curentă și cum se schimbă.
Un [obiect aplicație][application object] ține o stivă de limbi, `_.push(code)`
și `_.pop()` o mișcă, `with _.using(code):` se imbrichează, iar o
[strategie][strategy] găsește catalogul pentru un cod de limbă, așa încât
aplicația nu manevrează niciodată obiecte de catalog. Un server care trebuie să
producă text în mai multe limbi în cadrul unei singure unități de lucru — o
pagină pentru cititor, o notificare pentru cineva al cărui cont este setat
altfel — este exact cazul pentru care există asta.

Stiva trăiește pe acel obiect aplicație, pe care întregul proces îl împarte.
Două cereri care se suprapun împart deci o singură stivă, iar blocurile care nu
sunt strict imbricate *în timp* își dau unul altuia limba greșită:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Biblioteca de față păstrează aceeași capabilitate — legările se imbrichează și
se desfac la fel — într-o `ContextVar` în loc de o stivă partajată, așa că
întrepătrunderea de mai sus se rezolvă per task. Echivalentele se află pe
[Mai multe limbi deodată](guide.md#several-languages-at-once). Ce nu oferă este
căutarea catalogului după codul de limbă: tu treci un obiect translations, care
în cazul obișnuit înseamnă un singur apel `gettext.translation()`, iar
biblioteca standard ține în cache catalogul deja parsat.

## t-stringuri { #t-strings }

```python
tr(t"Hello {name}")
```

Catalogul vede tot `Hello {name}` și rămâne un catalog PO/MO obișnuit.
Diferența este ce anume *are voie să spună* o traducere, și cine verifică asta.

Biblioteca de față validează fiecare traducere față de substituenții mesajului
sursă înainte de randare, și acceptă nume goale și nimic altceva. Față de
`t"Hello {name}"`:

| O traducere care conține | este respinsă cu |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Respins nu înseamnă căzut: în mod implicit biblioteca jurnalizează un
avertisment și randează textul sursă, așa că un catalog prost nu doboară
niciodată aplicația —
[același contract pe care îl ține gettext însuși](guide.md#what-happens-when-a-catalog-is-wrong).

Formatarea rămâne acolo unde a fost scrisă, în cod:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nu ajunge niciodată la catalog, așa că nicio traducere nu îl poate
schimba și niciun traducător nu trebuie să se uite la el.

Încă o diferență ține de unelte: t-stringurile sunt sintaxă nouă, așa că
extragerea lor într-un `.pot` cere deocamdată un extractor care știe de
t-stringuri, precum cel pe care acest pachet îl
[oferă pentru Babel](extraction.md).

## Una lângă alta { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Substituentul are nume? | da | da | da | da |
| Poate un traducător să reordoneze substituenții? | da | da | da | da |
| De unde vin valorile? | dintr-o mapare explicită | din argumente explicite | din variabilele locale și globale ale apelantului, plus `extras` opțional | din valorile captate înăuntrul t-stringului |
| Poate catalogul să schimbe felul în care este formatată o valoare? | da | da | nu | nu |
| Poate catalogul să ajungă în interiorul obiectelor (acces la atribute)? | nu | da | da, cu nume cu punct | nu |
| O traducere *pierde* un substituent — ce se randează? | valoarea dispare pe tăcute | valoarea dispare pe tăcute | valoarea dispare pe tăcute | textul sursă, cu un avertisment ([în mod implicit](guide.md#what-happens-when-a-catalog-is-wrong)) |
| O traducere *adaugă* un substituent necunoscut — ce se randează? | o excepție | o excepție | substituentul rămâne vizibil ca text | textul sursă, cu un avertisment ([în mod implicit](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Sunt substituenții verificați la momentul randării? | nu | nu | nu | da (vezi mai jos) |
| Ce flag PO deduce Babel, pentru ca uneltele existente să valideze? | `python-format` | `python-brace-format` | niciunul | `python-brace-format` |
| Folosește cataloage PO/MO obișnuite? | da | da | da | da |
| Are nevoie de un extractor de sursă propriu? | nu | nu | nu | da, deocamdată |
| Unde trăiește „limba curentă”? | oriunde o pune aplicația | oriunde o pune aplicația | o stivă de coduri de limbă pe obiectul aplicație partajat | o `ContextVar`, per task sau per cerere |

Despre verificarea de la momentul randării: mesajelor la singular li se verifică
o potrivire exactă a substituenților. Și mesajelor la plural li se verifică,
față de [regula de reuniune/intersecție](spec.md) care permite ca formele de
plural ale unei limbi țintă să difere de cele ale sursei; verificarea mai
strictă, formă cu formă, rulează atunci când cataloagele sunt compilate
([Extragere](extraction.md)).

Rândul cu flagul de format este despre validarea conștientă de substituenți, nu
despre compatibilitatea cataloagelor. `niciunul` înseamnă că uneltele gettext
standard citesc și compilează în continuare mesajul, dar `msgfmt --check-format`
nu are nicio gramatică de substituenți `$` pe care să o aplice.

## Cât costă { #what-it-costs }

Un f-string nu poate fi folosit deloc în acest fel — până când vreo bibliotecă
apucă să vadă unul, el este deja un șir terminat, așa că a-l traduce înseamnă a
traduce un fragment. T-stringurile ([PEP 750]) țin separate textul static și
valorile, păstrând totodată o sintaxă asemănătoare f-stringurilor și legarea
explicită a valorilor. `$`-stringurile oferă deja o alternativă concisă, cu un
model diferit de legare și de eșec. `flufl.i18n` este un pachet matur, care
rulează pe Python 3.10 și mai nou; `gettext-tstrings` este deocamdată un alpha
și, pentru că t-stringurile sunt sintaxă nouă, cere Python 3.14 sau mai nou.

Celălalt cost este chiar restricția: o interpolare trebuie să fie un nume
simplu.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Aceasta este o constrângere reală. Împreună cu legarea valorilor dinspre sursă
și cu verificarea substituenților la rulare, ea împiedică șirurile din catalog
să evalueze expresii și păstrează numele substituenților pline de înțeles.

Cum a ajuns Python la această răscruce — două PEP-uri la zece ani distanță și
discuția din biblioteca standard care s-a închis fără un răspuns — este
povestit, cu surse, în [Context](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
