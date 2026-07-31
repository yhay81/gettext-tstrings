---
description: "T-eilučių perėmimas projekte, kuris jau turi gettext katalogus: kas lieka nepaliestas, kas tampa fuzzy ir kaip judėti po vieną iškvietimo vietą."
---

# Migracija

Jei jūsų projektas jau naudoja gettext, klausimai, lemiantys, ar šią biblioteką
įmanoma perimti, yra siauri: ar ji nepanaikina jūsų turimų katalogų, ar ji gali
sugyventi su kodu, kurio dar nesate pasiruošę keisti, ir kiek to perėjimo turi
įvykti iš karto. Atsakymai, pradedant trumpiausiu:

| Klausimas | Atsakymas |
| --- | --- |
| Ar esami `.po` ir `.mo` failai vis dar veikia? | Taip. Tie patys failai, tie patys įrankiai. |
| Ar seni ir nauji iškvietimai gali gyventi viename faile? | Taip, ir vienas ištraukiklio atvaizdis dengia abu. |
| Ar msgid pasikeičia? | Ne, jei einate nuo `.format()`. Taip, jei nuo `%`-formato. |
| Ar visas projektas turi persikelti iš karto? | Ne. Viena iškvietimo vieta yra visavertis pakeitimas. |
| O kaip Jinja, Django šablonai, JavaScript? | Nepaliesti, tie patys katalogai. |

Likusi šio puslapio dalis yra kiekvieno iš tų atsakymų smulkmenos.

## Nuo `.format()`: msgid nesikeičia { #from-format-the-msgid-does-not-change }

Tai atvejis, kai migracija kainuoja beveik nieko. `str.format` pranešimas ir
t-eilutės pranešimas išveda *tą patį* katalogo raktą, nes abiem atvejais raktas
yra tekstas su jame paliktu `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Taigi esamas vertimas lieka prikabintas. Pradedant nuo katalogo, kuriame yra

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

pakeiskite iškvietimą, ištraukite iš naujo ir atnaujinkite:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Grįžtantis įrašas skiriasi dviem metaduomenų eilutėmis ir daugiau niekuo —
žymos komentaru, įvardijančiu jį kaip t-eilutės pranešimą, ir pirminio kodo
eilutės numeriu:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Jokios `fuzzy` žymos, jokio vertimo iš naujo — nė viena kalba. Pranešimas
atvaizduojamas iškart:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` praneš, kad katalogai pasenę"

    To žymos komentaro ir pasislinkusių eilučių numerių pakanka, kad
    `pybabel update --check` pasakytų, jog katalogą reikia sugeneruoti iš
    naujo, nes jis lygina visą įrašą, o ne vien vertimą. Paleiskite tikrą
    `pybabel update` tame pačiame commit'e kaip ir kodo pakeitimą ir įtraukite
    katalogus kartu su juo — to paties įpročio jau prašo ir
    [CI vartai](workflow.md#what-ci-gates).

## Nuo `%`-formato: msgid keičiasi, todėl vertimai tampa fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf sintaksė gyvena pranešimo *viduje*, todėl ją pakeitus perrašomas katalogo
raktas. To apeiti neįmanoma, ir tai yra sąžininga `%(name)s` palikimo kaina:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` atpažįsta naują pranešimą kaip artimą pašalintojo giminaitį ir
perneša seną vertimą, pažymėdamas jį fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Apie tą būseną verta žinoti tris dalykus:

- **Veikimo metu niekas nelūžta.** Fuzzy įrašai į sukompiliuotą `.mo`
  neįtraukiami, todėl programa atvaizduoja pirminį pranešimą, kol žmogus poros
  nepatvirtina — [tas pats
  nusileidimas](workflow.md#the-cycle-after-the-first-translation), per kurį
  praeina bet kuris performuluotas pranešimas.
- **CI lieka žalias, kol jie fuzzy.** Vietaženklių tikrintuvas fuzzy įrašus
  praleidžia — lygiai kaip ir `msgfmt --check-format` — nes įrašas, kuris
  negali pasiekti veikimo aplinkos, neturėtų griauti kūrimo. Vos vertėjui
  nuėmus žymą, įrašas tikrinamas kaip bet kuris kitas — tad patvirtintame
  vertime likęs `%(name)s` pagaunamas būtent tada, kai jis kitaip pradėtų būti
  atvaizduojamas.
- **Sena `python-format` žyma keliauja kartu** ir turėtų būti ištrinta drauge su
  `fuzzy` žyma, kitaip `msgfmt --check-format` ir toliau taikys printf taisykles
  riestinių skliaustų formato pranešimui.

Vardiniams printf vietaženkliams taisymas yra mechaniškas — `%(name)s` tampa
`{name}`, ir daugiau niekas nejuda — tad didelis katalogas yra scenarijaus
praėjimas su paskesne vertėjo peržiūra, o ne vertimas iš naujo. Poziciniai `%s`
mechaniški nėra: jie neturi vardo, kurį būtų galima pernešti, o to vardo
parinkimas ir yra viso pakeitimo esmė.

Todėl migracija gali vykti tokiu tempu, kokį leidžia peržiūra: nekonvertuotas
fuzzy įrašas yra matomas darbo gabalas kataloge, o ne sugriautas kūrimas.

## Seni ir nauji iškvietimai sugyvena { #old-and-new-calls-coexist }

Ištraukiklis, skaitantis t-eilutes, skaito ir įprastus gettext iškvietimus,
todėl vienas atvaizdis dengia failą migracijos viduryje:

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

Abu pranešimai nutupia tame pačiame šablone, ir tik t-eilutės pranešimas neša
žymos komentarą, įjungiantį papildomą šios bibliotekos tikrinimą:

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

Jis atpažįsta `_()`, keturis standartinius gettext vardus, `tr()` / `ntr()`
sinonimus ir atidėtuosius `lazy_gettext()` / `lazy_pgettext()`. Jūsų pačių
pagalbinę funkciją reikia
[įvardyti atvaizdyje](extraction.md#registering-your-own-function-names).

Veikimo metu abu stiliai vienodai nepriklausomi: `gettext.translation()` grąžina
vieną vertimų objektą, o ir `_`, ir šios bibliotekos įėjimo vietos skaito iš jo.

## Kas nejuda { #what-does-not-move }

- **Šablonų kalbos.** Jinja2 `{% trans %}`, Django šablonų žymos ir jų Babel
  ištraukikliai toliau veikia nepakitę ir toliau maitina tuos pačius PO
  katalogus. T-eilutės yra Python sintaksė; jos taikomos Python pirminiam kodui.
- **Jūsų katalogų failai.** Jokio formato pakeitimo, jokio naujo failo, jokio
  konvertavimo žingsnio.
- **Jūsų vertimo platforma.** `.po` mainai identiški, o `python-brace-format`
  žyma, kurią neša t-eilutės pranešimas, yra ta pati žyma, kurią neša
  `.format()` pranešimas — tad vietaženklių kokybės kontrolė toliau veikia.
- **Ne Python kodas.** JavaScript ar C katalogas tame pačiame projekte lieka
  nepaliestas.

## Migracijos kontrolinis sąrašas { #a-migration-checklist }

1. Pridėkite `babel` priedą ten, kur veikia `pybabel`, ir pakeiskite `python`
   atvaizdį `babel.cfg` faile į `gettext_tstrings` metodą — tada vienas
   atvaizdis dengia abu stilius, o `-k` toliau veikia įprastiems iškvietimams.
2. Pirmiausia konvertuokite `.format()` iškvietimo vietas. Ištraukite iš naujo,
   paleiskite `pybabel update` ir įtraukite katalogus kartu su kodu; fuzzy įrašų
   tikėtis neverta.
3. Konvertuokite `%`-formato iškvietimo vietas tokiomis porcijomis, kokias
   pajėgsite peržiūrėti, perrašydami pernešus atsiradusius vietaženklius ir
   nuimdami `fuzzy` bei `python-format` žymas.
4. Sutvarkykite tai, ką apribojimas atmeta: interpoliacija turi būti paprastas
   vardas, tad `t"Hello {user.name}"` pirma tampa vietiniu kintamuoju. Tai
   iškvietimo vietos, o ne katalogo taisymas.
5. Kai šluostymas baigtas, įjunkite `strict = true` ištraukiklio atvaizdyje, kad
   pranešimas, kurio nepavyksta ištraukti, sugriautų
   [kūrimą](extraction.md#lenient-locally-strict-in-ci), o ne tyliai dingtų iš
   šablono.
6. Pridėkite veikimo meto patikrą iš [Realioje
   aplinkoje](workflow.md#what-ci-gates): atvaizduokite po vieną pranešimą
   kiekviena išsiunčiama kalba per griežtą `Translator`.

2 ir 3 žingsniai yra įprasti commit'ai. Niekam šiame sąraše nereikia vieno
didžiojo perjungimo dienos.
