---
description: "T-virkņu pārņemšana projektā, kuram jau ir gettext katalogi: kas paliek neskarts, kas kļūst fuzzy un kā pārvietoties pa vienai izsaukuma vietai."
---

# Migrācija

Ja jūsu projekts jau lieto gettext, jautājumi, kas izlemj, vai šī bibliotēka ir
pārņemama, ir šauri: vai tā padara nederīgus jūsu esošos katalogus, vai tā spēj
līdzāspastāvēt ar kodu, ko vēl neesat gatavi mainīt, un cik daudz no pārejas
jānotiek uzreiz. Atbildes, sākot ar īsākajām:

| Jautājums | Atbilde |
| --- | --- |
| Vai esošie `.po` un `.mo` faili joprojām strādā? | Jā. Tie paši faili, tie paši rīki. |
| Vai vecie un jaunie izsaukumi var dzīvot vienā failā? | Jā, un viens ekstraktora attēlojums sedz abus. |
| Vai msgid mainās? | No `.format()` — nē. No `%`-formāta — jā. |
| Vai visam projektam jāpārvietojas uzreiz? | Nē. Viena izsaukuma vieta ir derīga izmaiņa. |
| Kā ar Jinja, Django veidnēm, JavaScript? | Neskarti, tie paši katalogi. |

Pārējā lapas daļa ir detaļas aiz katras no tām.

## No `.format()`: msgid nemainās { #from-format-the-msgid-does-not-change }

Šis ir gadījums, kurā migrācija maksā gandrīz neko. `str.format` ziņojums un
t-virknes ziņojums atvasina *vienu un to pašu* kataloga atslēgu, jo abos
gadījumos atslēga ir teksts ar tajā atstāto `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Tātad esošais tulkojums paliek piesaistīts. Sākot no kataloga, kurā ir

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

nomainiet izsaukumu, ekstrahējiet no jauna un atjauniniet:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Ieraksts, kas nāk atpakaļ, atšķiras ar divām metadatu rindām un neko citu — ar
marķiera komentāru, kas to identificē kā t-virknes ziņojumu, un ar pirmkoda
rindas numuru:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Nekāda `fuzzy` karoga, nekādas pārtulkošanas nevienā valodā. Ziņojums
renderējas nekavējoties:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` ziņos, ka katalogi ir novecojuši"

    Šis marķiera komentārs un pārbīdītie rindu numuri ir pietiekami, lai
    `pybabel update --check` pateiktu, ka katalogs jāģenerē no jauna, jo tas
    salīdzina visu ierakstu, nevis tikai tulkojumu. Palaidiet īsto
    `pybabel update` tajā pašā commit, kurā ir koda izmaiņa, un iekļaujiet
    katalogus tajā pašā — tas ir tas pats ieradums, ko jau prasa
    [CI vārti](workflow.md#what-ci-gates).

## No `%`-formāta: msgid mainās, tāpēc tulkojumi kļūst fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf sintakse dzīvo ziņojuma *iekšienē*, tāpēc tās aizstāšana pārraksta
kataloga atslēgu. Apiet to nav iespējams, un tā ir godīgā cena par `%(name)s`
pamešanu:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` atpazīst jauno ziņojumu kā tuvu radinieku noņemtajam un
pārnes veco tulkojumu pāri, atzīmētu kā fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Par šo stāvokli jāzina trīs lietas:

- **Izpildlaikā nekas nesalūzt.** Fuzzy ieraksti kompilētajā `.mo` netiek
  iekļauti, tāpēc lietotne renderē avota ziņojumu, līdz cilvēks pāri
  apstiprina — [tā pati degradācija](workflow.md#the-cycle-after-the-first-translation),
  ko iziet jebkurš pārformulēts ziņojums.
- **CI paliek zaļš, kamēr tie ir fuzzy.** Vietturu pārbaudītājs fuzzy ierakstus
  izlaiž — tieši tāpat kā `msgfmt --check-format` —, jo ieraksts, kas nespēj
  nonākt līdz izpildlaikam, nedrīkst nogāzt būvējumu. Brīdī, kad tulkotājs
  karogu noņem, ieraksts tiek pārbaudīts tāpat kā jebkurš cits — tātad
  `%(name)s`, kas palicis apstiprinātā tulkojumā, tiek noķerts tieši tad, kad
  tas citādi sāktu renderēties.
- **Vecais `python-format` karogs brauc līdzi** un jādzēš kopā ar `fuzzy`
  karogu, citādi `msgfmt --check-format` turpinās piemērot printf noteikumus
  brace formāta ziņojumam.

Nosauktiem printf vietturiem labojums ir mehānisks — `%(name)s` kļūst par
`{name}`, un nekas cits nekustas —, tāpēc liels katalogs ir skriptēts gājiens,
kam seko tulkotāja pārskatīšana, nevis pārtulkošana. Pozicionālais `%s` nav
mehānisks: tam nav nosaukuma, ko pārnest, un tā izvēle ir visas izmaiņas jēga.

Tāpēc migrācija var virzīties tādā tempā, kādu atļauj pārskatīšana:
nepārveidots fuzzy ieraksts ir redzams darba gabals katalogā, nevis salauzts
būvējums.

## Vecie un jaunie izsaukumi līdzāspastāv { #old-and-new-calls-coexist }

Ekstraktors, kas lasa t-virknes, lasa arī parastos gettext izsaukumus, tāpēc
viens attēlojums sedz failu migrācijas vidū:

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

Abi ziņojumi nonāk vienā veidnē, un tikai t-virknes ziņojums nes marķiera
komentāru, kas ieslēdz šīs bibliotēkas papildu pārbaudi:

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

Tas atpazīst `_()`, četrus standarta gettext nosaukumus, `tr()` / `ntr()`
aizstājvārdus un atliktos `lazy_gettext()` / `lazy_pgettext()`. Jūsu paša
palīgs ir [jānosauc attēlojumā](extraction.md#registering-your-own-function-names).

Izpildlaikā abi stili ir vienlīdz neatkarīgi: `gettext.translation()` atgriež
vienu tulkojumu objektu, un gan `_`, gan šīs bibliotēkas ieejas punkti lasa no
tā.

## Kas nekustas { #what-does-not-move }

- **Veidņu valodas.** Jinja2 `{% trans %}`, Django veidņu tagi un to Babel
  ekstraktori turpina strādāt nemainīti un turpina barot tos pašus PO
  katalogus. T-virknes ir Python sintakse; tās attiecas uz Python pirmkodu.
- **Jūsu kataloga faili.** Nekādas formāta maiņas, nekāda jauna faila, nekāda
  konversijas soļa.
- **Jūsu tulkošanas platforma.** `.po` apmaiņa ir identiska, un
  `python-brace-format` karogs, ko nes t-virknes ziņojums, ir tas pats karogs,
  ko nes `.format()` ziņojums — tāpēc vietturu kvalitātes kontrole turpina
  strādāt.
- **Kods, kas nav Python.** JavaScript vai C katalogs tajā pašā projektā paliek
  neskarts.

## Migrācijas kontrolsaraksts { #a-migration-checklist }

1. Pievienojiet `babel` papildinājumu tur, kur darbojas `pybabel`, un nomainiet
   `python` attēlojumu `babel.cfg` failā uz `gettext_tstrings` metodi — viens
   attēlojums tad sedz abus stilus, un `-k` parastajiem izsaukumiem turpina
   strādāt.
2. Vispirms pārveidojiet `.format()` izsaukuma vietas. Ekstrahējiet no jauna,
   palaidiet `pybabel update` un iekļaujiet katalogus kopā ar kodu; fuzzy
   ierakstus negaidiet.
3. Pārveidojiet `%`-formāta izsaukuma vietas partijās, kurām varat panākt
   pārskatīšanu, pārrakstot pārnestos vietturus un noņemot `fuzzy` un
   `python-format` karogus.
4. Salabojiet to, ko ierobežojums noraida: interpolācijai jābūt kailam
   nosaukumam, tāpēc `t"Hello {user.name}"` vispirms kļūst par lokālu mainīgo.
   Tas ir izsaukuma vietas labojums, nevis kataloga.
5. Kad gājiens ir pabeigts, ieslēdziet `strict = true` ekstraktora attēlojumā,
   lai ziņojums, ko nav iespējams ekstrahēt, nogāž
   [būvējumu](extraction.md#lenient-locally-strict-in-ci), nevis pazūd no
   veidnes.
6. Pievienojiet izpildlaika pārbaudi no [Produkcijā](workflow.md#what-ci-gates):
   renderējiet vienu ziņojumu katrā piegādātajā valodā caur stingru
   `Translator`.

2. un 3. solis ir parasti commit. Nekam šajā sarakstā nav vajadzīga viena
lielā pārslēgšanās diena.
