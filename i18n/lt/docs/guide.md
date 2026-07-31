---
description: "Veikimo metu naudojama API: katalogo susiejimas, kalbos pagal užklausą, atidėtos eilutės ir tai, kaip pranešama apie sugadintą vertimą."
---

# Vadovas

Šis puslapis yra veikimo meto žinynas: viskas, ką jūsų *programos kodas* daro
su šia biblioteka, kai katalogai jau egzistuoja. Jei dar nematėte viso ciklo —
pažymėti, ištraukti, išversti, sukompiliuoti, paleisti — [pamoka](tutorial.md)
jį pereina vieną kartą per penkias minutes; katalogų kūrimas ir tikrinimas
aprašytas [Ištraukime](extraction.md), o kaip komanda tą ciklą sukioja —
atnaujinimo ciklai, CI, vertimo platformos — yra
[Realioje aplinkoje](workflow.md).

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

## Kas nutinka, kai katalogas klaidingas { #what-happens-when-a-catalog-is-wrong }

Jei vertimo vietaženkliai neatitinka pirminių — trūkstamas, nežinomas ar
performatuotas laukas, prasprūdęs pro patikrą iš ranka taisyto MO, tiekėjo
katalogo ar konvejerio, praleidžiančio tikrintuvą — pagal nutylėjimą atkuriamas
pirminis tekstas, o ne keliama klaida. Tai atkartoja paties gettext kontraktą,
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

## Kaip skaityti klaidos pranešimą { #reading-a-failure-message }

Šie pranešimai parašyti tam, kas gali dėl jų ką nors padaryti, o katalogo
atveju tai dažniau vertėjas nei programuotojas. Pranešti vien, kad `{name}`
trūksta, yra aklavietė, kai skaitytojas mato tuos simbolius prieš save, todėl
ten, kur vietaženklis atrodo esantis, bet jo nėra, pranešimas pasako kodėl.
Prieš pirminį `Hello {name}` kiekvienas iš šių atvejų pranešamas po antrašte
`translation does not match the source placeholders:`

| Vertime parašyta | Nurodoma priežastis |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (skliaustai aplink jį nėra ASCII `{` ir `}`) |
| `こんにちは {{name}}` | `{name}` is missing (parašyta `{{name}}`, o taip užrašomas literalus riestinis skliaustas) |
| `こんにちは name` | `{name}` is missing (vardas yra, bet ne skliaustuose) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Simboliai, kurių pamatyti neįmanoma, sulaukia atskiro elgesio. Nedalus tarpas
skliaustų viduje yra tai, ką pagamina įvesties metodas ir ko neparodo joks
redaktorius, todėl pranešimas jį išspausdina kodo pozicija, užuot įvardijęs
simbolį, kurio skaitytojas nerastų:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Vardas, kurio raidės maišo skirtingas rašto sistemas — homoglifų atvejis, kai
kirilicos `а` neatskiriama nuo lotyniškos — parodomas dukart: kartą skaitomai,
kartą su kaitos sekomis, nes tik ši forma leidžia jas atskirti:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Tas pats atskyrimas taikomas, kai graikiškas ar kirilinis vardas, parašytas
ištisai viena rašto sistema, konfliktuoja su ASCII pirminiu vardu — įskaitant
vienos raidės atvejį: lotyniška `a` prieš kirilinę `а`.

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
