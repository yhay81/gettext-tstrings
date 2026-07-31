---
description: "Keyrslutíma-API-ið: að binda þýðingaskrá, tungumál eftir beiðni, frestaðir strengir og hvernig biluð þýðing er tilkynnt."
---

# Handbók

Þessi síða er uppflettiritið um keyrslutímann: allt sem *forritskóðinn þinn*
gerir með þessu safni þegar þýðingaskrár eru til. Hafir þú ekki enn séð alla
hringrásina — merkja, draga út, þýða, vistþýða, keyra — þá gengur
[kennsluefnið](tutorial.md) hana einu sinni á fimm mínútum; að búa til og
staðfesta þýðingaskrár er tekið fyrir í [Útdrætti](extraction.md), og hvernig
teymi heldur hringrásinni gangandi — uppfærsluferli, CI, þýðingavettvangar —
er [Í rekstri](workflow.md).

## Að binda þýðingaskrá { #binding-a-catalog }

Ráðlagða lagið speglar klasabundna notkun gettext: bittu eitt staðlað
þýðingahlutfall einu sinni og notaðu kallanlega vinnsluhlutinn sem `_`.

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

Föllin á einingarsviði fylgja nöfnum staðalsafnsins og kallvenju þess um
viðföng eingöngu eftir stöðu:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` og `ntr` eru nákvæm samheiti `gettext` og `ngettext`.

## Tungumál eftir beiðni { #per-request-language }

Vefumgjörð velur tungumál fyrir hverja beiðni. Bittu þýðingar beiðninnar við
núverandi samhengi og hvert kall á einingarsviði leysist yfir í það
tungumál, með öruggum hætti þvert á samhliða beiðnir:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` bindur án `with`-blokkar, fyrir umgjarðir
sem stýra líftíma beiðninnar sjálfar; `get_translations()` les núverandi
bindingu. Skýrt `translations=`-viðfang gengur alltaf framar samhenginu, og
óbundið samhengi fellur aftur í altækt uppsettu gettext-föllin úr
staðalsafninu. Útfærð dæmi fyrir Flask og ASGI-millilag eru á síðunni
[Í rekstri](workflow.md#binding-a-language-at-runtime).

## Frestuð þýðing { #deferred-translation }

t-strengur grípur gildi sín strax, sem er rangt fyrir streng sem er
skilgreindur við innflutning — merking á eyðublaði, gildi í talnaupptalningu,
fasti á einingarsviði — og þarf að birtast á því tungumáli sem er virkt þegar
hann er *notaður*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` birtist gegnum `str()`, `format()` og f-strengi, og telst jafn
birtum texta sínum.

!!! note "Af ásettu ráði ekki tætanlegt"

    Texti `LazyString` veltur á virka tungumálinu, svo tætigildi myndi
    breytast við tungumálaskipti og skemma hljóðlaust hvert mengi eða
    orðabók sem geymdi hann. Kallaðu á `str()` fyrst ef þú þarft lykil.

`strict` er ákveðið þar sem skilaboðin eru skrifuð, ekki þar sem þau eru birt:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Frestaður strengur er birtur þar sem hann er á endanum notaður — inni í
sniðmáti, í eyðublaði, í línu í atburðaskrá — og sá staður veit sjaldnast
hvort um prófkeyrslu eða rekstur er að ræða. Að gefa `strict=True` við
skilgreininguna er það sem lætur sama valið um
[hávært í CI, eftirgefanlegt í rekstri](#what-happens-when-a-catalog-is-wrong)
gilda líka um streng sem er ekki birtur á kallstað sínum.

Fleirtölumyndir velta á fjölda sem er þekktur á keyrslutíma, svo birtu þær
strax með `ngettext` þar sem fjöldinn er kunnur.

## Mörg tungumál í einu { #several-languages-at-once }

Ein beiðni þarf oft fleiri en eitt tungumál: síða sem er birt fyrir lesandann
og setur um leið tilkynningu í röð til reiknings sem er stilltur á annað, eða
samantekt sem vitnar í hvern þátttakanda á hans eigin. Bindingar hreiðrast, og
þegar innri blokkinni sleppir tekur sú ytri aftur við.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Þegar listi af viðtakendum á í hlut vinna frestaðir strengir verkið:
skilaboðin eru skrifuð einu sinni, við innflutning, og birt einu sinni fyrir
hvert tungumál.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Bindingin er `ContextVar`, ekki stafli á sameiginlegum hlut, svo að beiðnir
sem skarast geta ekki gripið tungumál hver annarrar — þar með talið tilvikið
þar sem þær *yfirgefa* blokkirnar sínar í sömu röð og þær gengu inn í þær, en
það er einmitt fléttan sem stafli af þessu tagi ræður ekki við. Það er ódýrt
að hlaða þýðingaskrá fyrir hvert tungumál: `gettext.translation()` þáttar
hverja `.mo`-skrá einu sinni og réttir út afrit sem deila þáttuðu skránni.

!!! warning "Vinnuþráður byrjar óbundinn"

    Ber `threading.Thread`, eða `ThreadPoolExecutor.submit`, byrjar með nýju
    samhengi og erfir ekki bindinguna — kallið fellur þá aftur í altæku
    gettext-þýðingaskrá ferlisins. Berðu samhengið yfir með skýrum hætti:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` gerir þetta þegar fyrir þig.

## Hvað gerist þegar þýðingaskrá er röng { #what-happens-when-a-catalog-is-wrong }

Ef staðgenglar þýðingar stemma ekki við frumtextann — reitur sem vantar, er
óþekktur eða hefur fengið nýtt snið og slapp gegnum athugunina, úr
handritaðri MO-skrá, þýðingaskrá frá þriðja aðila eða keðju sem sleppir
athuguninni — þá er sjálfgefið að endurgera frumtextann fremur en að varpa.
Þetta speglar samning gettext sjálfs um að léleg þýðingaskrá brjóti aldrei
forritið.

Þegar `Hello {name}` er þýtt sem `こんにちは {nombre}` tekst birtingin og ein
viðvörun fer í atburðaskrárrit `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Viðvörunin kemur einu sinni fyrir hver skilaboð og hvert mynstur, ekki einu
sinni við hverja birtingu, svo að biluð færsla í þýðingaskrá flæðir ekki yfir
atburðaskrána.

Veldu að falla hávært fyrir prófanir og CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Sama uppfletting varpar þá, með sömu setningu án helmingsins um „using source
text“:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Að lesa villuboð { #reading-a-failure-message }

Þessi skilaboð eru skrifuð fyrir þann sem getur brugðist við þeim, og þegar
þýðingaskrá á í hlut er það oftar þýðandi en forritari. Að tilkynna aðeins að
`{name}` vanti er blindgata þegar lesandinn sér þá stafi fyrir framan sig, svo
að þar sem staðgengill sýnist vera til staðar en er það ekki, segja skilaboðin
hvers vegna. Gagnvart frumtextanum `Hello {name}` er hvert eftirfarandi
tilkynnt undir `translation does not match the source placeholders:`

| Þýðingin segir | Ástæðan sem hún gefur |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Stafir sem ekki sjást fá sína eigin meðferð. Fast bil inni í slaufusvigunum er
eitthvað sem innsláttaraðferð framleiðir og enginn ritill sýnir, svo að
skilaboðin prenta það eftir kóðapunkti fremur en að nefna staf sem lesandinn
finnur ekki:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nafn þar sem stafirnir blanda ritkerfum — samstöfunartilvikið, þar sem
kýrillískt `а` er ógreinanlegt frá því latneska — er sýnt tvisvar, einu sinni
læsilega og einu sinni með escape-ritun, sem er eina myndin sem greinir þau
tvö að:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Sama aðgreining á við þegar grískt eða kýrillískt nafn, ritað alfarið í einu
letri, rekst á ASCII-nafn í frumtextanum, þar með talið tilvikið með
latneska `a` og kýrillíska `а` í einum staf.

## Að birta mynstur án þýðingaskrár { #rendering-a-pattern-without-a-catalog }

`compile_template` opinberar sama vélbúnað einu lagi neðar: það breytir
t-streng í msgid hans ásamt bundnu mengi gilda, og birtir hvaða mynstur sem
þú réttir því.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` athugar eftir sömu reglum og **varpar alltaf** ef ekki stemmir. Hér
er enginn eftirgefanlegur hamur: eftirgefanleikinn er til svo að uppfletting
í *þýðingaskrá* geti hrörnað yfir í frumtextann, og mynstur sem þú réttir
sjálfur hefur ekkert til að hrörna frá.

## Öryggi og umfang { #safety-and-scope }

Þetta er gilt:

```python
tr(t"Hello {name}")
```

Þessu er hafnað af ásettu ráði:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Reiknaðu fyrst út merkingarbært gildi:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Takmörkunin skilar stöðugum lyklum í þýðingaskrá, gefur þýðendum gagnleg nöfn
og kemur í veg fyrir að þýddur strengur verði að segðamáli.

Ábyrgðin nær til *byggingar og sniðs*: þýðing er aldrei reiknuð út og getur
aldrei bætt við aðgangi að eigindum, köllum, umbreytingum eða sniðlýsingum.
Tvennt er áfram á ábyrgð kallandans, nákvæmlega eins og með gettext úr
staðalsafninu — **escape-ritun** á birtu úttaki fyrir viðtakanda þess (HTML,
skel, skjáhermi) og **heilleiki þýðingaskrárinnar**, því fjandsamleg
þýðingaskrá getur endurtekið staðgengil til að magna upp stærð úttaksins, sem
er innbyggt í hverja i18n-aðferð sem byggir á staðgenglum.
