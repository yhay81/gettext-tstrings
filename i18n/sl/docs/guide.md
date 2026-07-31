---
description: "API med izvajanjem: vezava kataloga, jezik na zahtevo, odloženi nizi in kako se sporoči pokvarjen prevod."
---

# Vodnik

Ta stran je referenca za čas izvajanja: vse, kar vaša *aplikacijska koda*
počne s to knjižnico, ko katalogi že obstajajo. Če celotne zanke — označi,
izvleci, prevedi, kompiliraj, zaženi — še niste videli, jo
[vadnica](tutorial.md) prehodi enkrat v petih minutah; ustvarjanje in
preverjanje katalogov pokriva [Ekstrakcija](extraction.md), kako pa ekipa to
zanko vrti naprej — cikli posodobitev, CI, prevajalske platforme —, je
opisano v [V produkciji](workflow.md).

## Vezava kataloga { #binding-a-catalog }

Priporočena oblika zrcali gettextovo razredno rabo: standardni prevajalni
objekt vežite enkrat in klicljivi obdelovalec uporabljajte kot `_`.

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

Funkcije na ravni modula sledijo imenom iz standardne knjižnice in njenemu
izključno pozicijskemu klicnemu dogovoru:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` in `ntr` sta natančna vzdevka za `gettext` in `ngettext`.

## Jezik na zahtevo { #per-request-language }

Spletno ogrodje izbere jezik za vsako zahtevo posebej. Prevode zahteve vežite
na trenutni kontekst in vsak klic na ravni modula se razreši v ta jezik, varno
tudi pri sočasnih zahtevah:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` veže brez bloka `with`, za ogrodja, ki
življenjski cikel zahteve upravljajo sama; `get_translations()` prebere
trenutno vezavo. Izrecni argument `translations=` vedno premaga kontekst,
nevezan kontekst pa se zateče h globalno nameščenim funkcijam gettext iz
standardne knjižnice. Razdelana primera za Flask in vmesno programje ASGI sta
na strani [V produkciji](workflow.md#binding-a-language-at-runtime).

## Odloženo prevajanje { #deferred-translation }

T-niz svoje vrednosti ujame takoj, kar je napačno za niz, določen ob uvozu —
oznako obrazca, vrednost naštevnega tipa, modulsko konstanto —, ki se mora
izrisati v tistem jeziku, ki je dejaven ob njegovi *rabi*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` se izriše prek `str()`, `format()` in f-nizov ter je enak svojemu
izrisanemu besedilu.

!!! note "Namenoma nezgoščljiv"

    Besedilo objekta `LazyString` je odvisno od dejavnega jezika, zato bi se
    zgostitev ob zamenjavi jezika spremenila in tiho pokvarila vsako množico ali
    slovar, ki ga hrani. Če potrebujete ključ, najprej pokličite `str()`.

O `strict` se odloči tam, kjer je sporočilo zapisano, ne tam, kjer se izriše:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Odloženi niz se izriše tam, kjer je nazadnje uporabljen — znotraj predloge,
obrazca, dnevniške vrstice —, in to mesto le redko ve, ali gre za testni tek ali
za produkcijo. Prav `strict=True` ob določitvi je tisto, kar omogoči, da ista
izbira [glasno v CI, prizanesljivo v produkciji](#what-happens-when-a-catalog-is-wrong)
velja tudi za niz, ki se ne izriše na svojem klicnem mestu.

Množinske oblike so odvisne od števila med izvajanjem, zato jih tam, kjer je
število znano, izrišite takoj z `ngettext`.

## Več jezikov hkrati { #several-languages-at-once }

Ena sama zahteva pogosto potrebuje več kot en jezik: stran, izrisana za bralca,
ki hkrati uvrsti v vrsto obvestilo za račun, nastavljen na drug jezik, ali
povzetek, ki vsakega udeleženca navede v njegovem lastnem. Vezave se gnezdijo,
izhod iz notranjega bloka pa obnovi zunanjega.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Pri seznamu prejemnikov delo opravijo odloženi nizi: sporočilo je zapisano
enkrat, ob uvozu, izriše pa se enkrat za vsak jezik.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Vezava je `ContextVar` in ne sklad na deljenem objektu, zato prekrivajoče se
zahteve ne morejo pobrati jezika druga drugi — tudi tedaj ne, kadar svoje bloke
*zapustijo* v istem vrstnem redu, kot so vanje vstopile, kar je prav
prepletanje, ki ga sklad zgreši. Nalaganje kataloga za vsak jezik je poceni:
`gettext.translation()` vsak `.mo` razčleni enkrat in razdaja kopije, ki si
razčlenjeni katalog delijo.

!!! warning "Delovna nit se začne nevezana"

    Gola `threading.Thread` ali `ThreadPoolExecutor.submit` se začne s svežim
    kontekstom in vezave ne podeduje — klic se zateče h globalnemu gettextovemu
    katalogu procesa. Kontekst prenesite izrecno:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` to za vas stori že sam.

## Kaj se zgodi, kadar je katalog napačen { #what-happens-when-a-catalog-is-wrong }

Če se ograde prevoda ne ujemajo z izvornimi — manjkajoče, neznano ali
preoblikovano polje, ki se je izmuznilo preverjanju, iz ročno urejenega MO, iz
prevzetega kataloga ali iz cevovoda, ki preskoči preverjevalnik —, je privzeti
odziv, da se ponovi izvorno besedilo, ne pa da se sproži izjema. To zrcali
gettextov lastni dogovor, da slab katalog nikoli ne pokvari aplikacije.

Kadar je `Hello {name}` preveden kot `こんにちは {nombre}`, izris uspe, v
dnevnik `gettext_tstrings` pa gre eno opozorilo:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Opozorilo se sproži enkrat na sporočilo in vzorec, ne enkrat na izris, tako da
pokvarjen katalogni vnos ne preplavi dnevnika.

Za teste in CI se lahko odločite za glasno odpoved:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Isto iskanje tedaj sproži izjemo z isto povedjo, le brez polovice o »using
source text«:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Kako brati sporočilo o napaki { #reading-a-failure-message }

Ta sporočila so napisana za tistega, ki lahko ukrepa, pri težavi s katalogom pa
je to pogosteje prevajalec kot programer. Sporočiti zgolj, da `{name}` manjka,
je slepa ulica, kadar bralec te znake vidi pred sabo, zato tam, kjer je ograda
videti navzoča, pa ni, sporočilo pove tudi zakaj. Glede na izvirnik
`Hello {name}` se vsaka od naslednjih javi pod
`translation does not match the source placeholders:`

| Prevod pravi | Naveden razlog |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` manjka (oklepaja okoli njega nista znaka ASCII `{` in `}`) |
| `こんにちは {{name}}` | `{name}` manjka (zapisan je kot `{{name}}`, kar je ubežni zapis dobesednega oklepaja) |
| `こんにちは name` | `{name}` manjka (ime se pojavi, a ne znotraj oklepajev) |
| `こんにちは {名前}` | `{name}` manjka; `{名前}` ni v izvornem sporočilu |

Znaki, ki jih ni mogoče videti, so obravnavani posebej. Nedeljivi presledek
znotraj oklepajev je nekaj, kar proizvede vnosna metoda in česar noben
urejevalnik ne pokaže, zato ga sporočilo izpiše po kodni točki, namesto da bi
poimenovalo znak, ki ga bralec ne more najti:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ime, katerega črke mešajo pisave — primer homoglifa, kjer cirilski `а` ni
razločljiv od latinskega —, je prikazano dvakrat, enkrat berljivo in enkrat
ubežno zapisano, kar je edina oblika, ki oba loči:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Isto razdvoumljanje velja, kadar grško ali cirilsko ime, zapisano povsem v eni
pisavi, trči z izvornim imenom v ASCII, vključno z enočrkovnim primerom
latinskega `a` proti cirilskemu `а`.

## Izris vzorca brez kataloga { #rendering-a-pattern-without-a-catalog }

`compile_template` isto strojevje razkrije eno raven nižje: t-niz spremeni v
njegov msgid in vezano množico vrednosti ter izriše kateri koli vzorec, ki mu
ga izročite.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` preverja po istih pravilih in ob neujemanju **vedno sproži izjemo**.
Prizanesljivega načina tu ni: prizanesljivost obstaja zato, da se lahko
iskanje po *katalogu* poslabša do izvornega besedila, vzorec, ki ste ga izročili
sami, pa nima od česa poslabšati.

## Varnost in obseg { #safety-and-scope }

To je veljavno:

```python
tr(t"Hello {name}")
```

To je zavrnjeno namenoma:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Najprej izračunajte smiselno vrednost:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Omejitev daje stabilne katalogne ključe, prevajalcem uporabna imena in
preprečuje, da bi preveden niz postal izrazni jezik.

Jamstvo je omejeno na *zgradbo in oblikovanje*: prevod se nikoli ne ovrednoti
in nikoli ne more dodati dostopa do atributov, klicev, pretvorb ali formatnih
specifikacij. Dvoje ostaja odgovornost klicatelja, natanko kot pri gettextu iz
standardne knjižnice — **ubežno zapisovanje** izrisanega izhoda za njegov
ponor (HTML, lupina, terminal) in **celovitost kataloga**, saj lahko sovražen
katalog ogrado ponovi in tako napihne velikost izhoda, kar je lastno vsakemu
i18n, ki temelji na ogradah.
