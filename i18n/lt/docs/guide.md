---
description: "Veikimo metu naudojama API: kurią įėjimo vietą rinktis, katalogo susiejimas, kalbos pagal užklausą, atidėtos eilutės, lokalę atitinkančios reikšmės ir tai, kaip pranešama apie sugadintą vertimą."
---

# Vadovas

Šis puslapis yra veikimo meto žinynas: viskas, ką jūsų *programos kodas* daro
su šia biblioteka, kai katalogai jau egzistuoja. Jei dar nematėte viso ciklo —
pažymėti, ištraukti, išversti, sukompiliuoti, paleisti — [pamoka](tutorial.md)
jį pereina vieną kartą per penkias minutes; katalogų kūrimas ir tikrinimas
aprašytas [Ištraukime](extraction.md), o kaip komanda tą ciklą sukioja —
atnaujinimo ciklai, CI, vertimo platformos — yra
[Realioje aplinkoje](workflow.md).

## Kurią įėjimo vietą rinktis? { #which-entry-point-should-i-use }

Paketas siūlo kelis būdus pranešimui išversti, nes programos kalbą susieja
keliais skirtingais būdais. Rinkitės pagal tai, kaip jūsų programa nusprendžia,
kokia kalba ji kalba:

| Jūsų padėtis | Naudokite |
| --- | --- |
| Viena kalba visam procesui — CLI, darbalaukio programa, scenarijus | `Translator`, kviečiamas kaip `_` |
| Po kalbą kiekvienai užklausai ar asinchroninei užduočiai — žiniatinklio programa | `use_translations()` aplink darbą, tada `tr()` |
| Pranešimas, apibrėžtas importo metu — formos etiketė, enum, konstanta | `lazy_gettext()` arba `lazy_pgettext()` |
| Kiekis lemia formuluotę | `ngettext()` / `npgettext()` bet kuria iš aukščiau nurodytų formų |
| Šablono atvaizdavimas visai be katalogo | `compile_template()` |

Visa, kas žemiau, yra tie penki dalykai ta pačia tvarka.

## Katalogo susiejimas { #binding-a-catalog }

Rekomenduojama forma atkartoja gettext klasėmis grįstą naudojimą: vieną kartą
susieti standartinį vertimo objektą ir naudoti iškviečiamą apdorotoją kaip `_`.

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

Modulio lygmens funkcijos laikosi standartinės bibliotekos pavadinimų ir jos
tik pozicinių argumentų iškvietimo tvarkos:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` ir `ntr` yra tikslūs `gettext` ir `ngettext` sinonimai.

## Kalba pagal užklausą { #per-request-language }

Žiniatinklio karkasas kalbą parenka kiekvienai užklausai. Susiekite užklausos
vertimus su dabartiniu kontekstu, ir kiekvienas modulio lygmens iškvietimas
išsispręs į tą kalbą — saugiai net ir lygiagrečioms užklausoms:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` susieja be `with` bloko — karkasams, kurie
patys tvarko užklausos gyvavimo ciklą; `get_translations()` nuskaito dabartinį
susiejimą. Aiškiai nurodytas `translations=` argumentas visada nugali
kontekstą, o nesusietas kontekstas grįžta prie standartinės bibliotekos
globaliai įdiegtų gettext funkcijų. Išnagrinėti Flask ir ASGI tarpinės
programinės įrangos pavyzdžiai yra puslapyje
[Realioje aplinkoje](workflow.md#binding-a-language-at-runtime).

## Atidėtas vertimas { #deferred-translation }

T-eilutė savo reikšmes pagauna iš karto, o tai netinka eilutei, apibrėžtai
importavimo metu — formos etiketei, išvardijimo reikšmei, modulio konstantai —
kuri turi būti atvaizduota ta kalba, kuri aktyvi jos *panaudojimo* metu.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` atvaizduojama per `str()`, `format()` ir f-eilutes, o lygybėje
prilygsta savo atvaizduotam tekstui.

!!! note "Tyčia neturi maišos"

    `LazyString` tekstas priklauso nuo aktyvios kalbos, todėl maiša pasikeistų
    perjungus kalbą ir tyliai sugadintų bet kurią ją laikančią aibę ar žodyną.
    Jei reikia rakto, pirma iškvieskite `str()`.

`strict` nusprendžiama ten, kur pranešimas parašomas, o ne ten, kur jis
atvaizduojamas:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Atidėta eilutė atvaizduojama ten, kur galiausiai panaudojama — šablone, formoje,
žurnalo įraše — o ta vieta retai žino, ar tai testų paleidimas, ar reali
aplinka. Perdavus `strict=True` apibrėžimo vietoje, tas pats
[garsiai CI, atlaidžiai realioje aplinkoje](#what-happens-when-a-catalog-is-wrong)
pasirinkimas galioja ir eilutei, kuri atvaizduojama ne savo kvietimo vietoje.

Daugiskaitos formos priklauso nuo veikimo meto skaičiaus, todėl jas
atvaizduokite iš karto su `ngettext` ten, kur skaičius žinomas.

## Kelios kalbos vienu metu { #several-languages-at-once }

Vienai užklausai neretai reikia daugiau nei vienos kalbos: puslapis
atvaizduojamas skaitytojui, o kartu į eilę statomas pranešimas paskyrai,
kuriai nustatyta kita kalba, arba santrauka, cituojanti kiekvieną dalyvį jo
paties kalba. Susiejimai dedami vienas į kitą, o išėjus iš vidinio bloko
atkuriamas išorinis.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Einant per gavėjų sąrašą darbą atlieka atidėtos eilutės: pranešimas parašomas
vieną kartą, importavimo metu, ir atvaizduojamas po kartą kiekvienai kalbai.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Susiejimas yra `ContextVar`, o ne dėklas, laikomas bendrame objekte, todėl
persidengiančios užklausos negali pasigriebti viena kitos kalbos — įskaitant
atvejį, kai jos iš savo blokų *išeina* ta pačia tvarka, kuria į juos įėjo:
būtent šį persipynimą dėklas apdoroja klaidingai. Įkelti katalogą kiekvienai
kalbai pigu: `gettext.translation()` kiekvieną `.mo` perskaito vieną kartą ir
dalija kopijas, kurios naudoja tą patį perskaitytą katalogą.

!!! warning "Ar darbinė gija paveldi susiejimą, priklauso nuo darinio"

    Plika `threading.Thread` ar `ThreadPoolExecutor.submit` pradeda arba nuo
    iškvietėjo konteksto kopijos, arba nuo tuščio, o kuris iš jų —
    `sys.flags.thread_inherit_context`: laisvų gijų dariniuose jis pagal
    nutylėjimą teisingas, visur kitur — klaidingas. Todėl tas pats kodas su
    3.14t atvaizduoja susietą kalbą, o su 3.14 — proceso globalų katalogą.
    Perduokite kontekstą, užuot pasikliovę numatytąja elgsena:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` tai už jus jau padaro.

## Lokalę atitinkančios reikšmės { #locale-aware-values }

Ši biblioteka sprendžia, *kur* reikšmė atsiranda išverstame pranešime. Pačios
reikšmės ji nelokalizuoja. `{amount:,.2f}` yra Python formato specifikacija su
fiksuota elgsena — kablelis kas tris skaitmenis ir taškas prieš dešimtaines —
ir ji pagamina tuos pačius simbolius, kad ir kokia kalba būtų pranešimas:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Vokiečiai tą skaičių rašo `1.234,50`, prancūzai `1 234,50`, o hindi kalboje
`1234567` grupuojamas kaip `12,34,567`, o ne `1,234,567`. Skaičiai, valiutos,
datos, laikai ir matavimo vienetai priklauso [Babel][babel-numbers]. Pirma
suformatuokite reikšmę, tada įdėkite jau baigtą eilutę:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Skaičiuojamame pranešime skaičius atlieka du darbus — parenka daugiskaitos formą
ir pasirodo tekste — o lokalizuojamas tik antrasis. Atrankai palikite žalią
kiekį, o rodymui perduokite suformatuotą eilutę:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatavimas prieš iškvietimą yra ir tai, kas laiko formato specifikaciją už
katalogo ribų: vertėjas mato baigtą teksto gabalą, o ne skaičių su nurodymais,
kaip jį atvaizduoti.

## Kas nutinka, kai katalogas klaidingas { #what-happens-when-a-catalog-is-wrong }

Jei vertimo vietaženkliai neatitinka pirminių — trūkstamas, nežinomas ar
performatuotas laukas, prasprūdęs pro patikrą iš ranka taisyto MO, tiekėjo
katalogo ar konvejerio, praleidžiančio tikrintuvą — pagal nutylėjimą
atvaizduojamas pirminis pranešimas, o ne keliama klaida. Tai atkartoja paties gettext kontraktą,
kad blogas katalogas niekada nesulaužo programos.

Kai `Hello {name}` išverstas kaip `こんにちは {nombre}`, atvaizdavimas pavyksta,
o į `gettext_tstrings` žurnalą patenka vienas įspėjimas:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Įspėjimas suveikia po kartą kiekvienam pranešimui ir šablonui, o ne kiekvieną
atvaizdavimą, todėl sugadintas katalogo įrašas neužtvindo žurnalo.

Testams ir CI galite pasirinkti garsų lūžimą:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Ta pati paieška tada kelia klaidą, nešančią tą patį sakinį, tik be dalies
„using source text“:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Šie pranešimai parašyti tam, kas gali dėl jų ką nors padaryti, o katalogo
atveju tai dažniau vertėjas nei programuotojas — todėl ten, kur vietaženklis
atrodo esantis, bet jo nėra, pranešimas paaiškina kodėl, o ne pakartoja, kad jo
trūksta. Viso pločio skliaustai, padvigubintas `{{name}}`, nematomas nedalus
tarpas, kirilicos raidė tarp lotyniškų: kiekvienas turi savo formuluotę, o
sąrašas su pavyzdžiais yra puslapyje
[Vertėjams](translators.md#reading-a-failure-message). Tas puslapis parašytas
taip, kad jį būtų galima perduoti tam, kas redaguoja `.po`.

## Šablono atvaizdavimas be katalogo { #rendering-a-pattern-without-a-catalog }

`compile_template` atveria tą pačią mechaniką vienu lygmeniu žemiau: ji paverčia
t-eilutę jos msgid'u ir susietų reikšmių rinkiniu bei atvaizduoja bet kurį jai
paduotą šabloną.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` tikrina pagal tas pačias taisykles ir neatitikus **visada kelia
klaidą**. Nuolaidaus režimo čia nėra: nuolaidumas egzistuoja tam, kad *katalogo*
paieška galėtų nusileisti iki pirminio teksto, o šablonas, kurį patys perdavėte,
neturi nuo ko nusileisti.

## Sauga ir apimtis { #safety-and-scope }

Šitaip galima:

```python
tr(t"Hello {name}")
```

O šitaip tyčia neleidžiama:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Pirma apskaičiuokite prasmingą reikšmę:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Šis apribojimas duoda stabilius katalogo raktus, suteikia vertėjams naudingus
vardus ir neleidžia išverstai eilutei tapti reiškinių kalba.

Garantija apima *struktūrą ir formatavimą*: vertimas niekada nėra
apskaičiuojamas ir niekada negali pridėti prieigos prie atributų, iškvietimų,
konversijų ar formato specifikacijų. Du dalykai lieka kviečiančiojo atsakomybe —
lygiai kaip ir su standartinės bibliotekos gettext: atvaizduotos išvesties
**ekranavimas** pagal jos paskirties vietą (HTML, apvalkalas, terminalas) ir
**katalogo vientisumas**, nes priešiškas katalogas gali kartoti vietaženklį,
kad išpūstų išvesties dydį, o tai būdinga bet kokiam vietaženkliais grįstam
i18n.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
