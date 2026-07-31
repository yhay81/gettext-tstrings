---
description: "Mabwysiadu llinynnau-t mewn prosiect sydd eisoes â chatalogau gettext: beth sy'n goroesi heb ei gyffwrdd, beth sy'n mynd yn fuzzy, a sut i symud un safle galw ar y tro."
---

# Mudo

Os yw eich prosiect eisoes yn defnyddio gettext, cwestiynau cul yw'r rhai sy'n
penderfynu a ellir mabwysiadu'r llyfrgell hon: a yw'n annilysu'r catalogau sydd
gennych, a all gydfodoli â'r cod nad ydych yn barod i'w newid, a faint o'r
symud sydd raid digwydd ar unwaith. Yr atebion, y byrraf yn gyntaf:

| Cwestiwn | Ateb |
| --- | --- |
| A yw'r ffeiliau `.po` ac `.mo` sy'n bodoli'n dal i weithio? | Ydynt. Yr un ffeiliau, yr un offer. |
| A all hen alwadau a rhai newydd fyw mewn un ffeil? | Gallant, ac mae un mapio echdynnwr yn ymdrin â'r ddau. |
| A yw'r msgid yn newid? | Nid o `.format()`. Ydy o fformat-`%`. |
| A raid i'r prosiect cyfan symud ar unwaith? | Na raid. Mae un safle galw'n newid dilys. |
| Beth am Jinja, templedi Django, JavaScript? | Heb eu cyffwrdd, yr un catalogau. |

Y manylion y tu ôl i bob un o'r rheini yw gweddill y dudalen hon.

## O `.format()`: nid yw'r msgid yn newid { #from-format-the-msgid-does-not-change }

Dyma'r achos lle nad yw mudo'n costio nemor ddim. Mae neges `str.format` a
neges llinyn-t yn deillio'r *un* allwedd gatalog, am mai'r testun â `{name}`
wedi'i adael ynddo yw'r allwedd y naill ffordd neu'r llall:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Felly mae'r cyfieithiad sy'n bodoli'n aros ynghlwm. Gan gychwyn o gatalog sy'n
dal

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

newidiwch yr alwad, ail-echdynnwch, a diweddarwch:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Mae'r cofnod sy'n dod yn ôl yn gwahaniaethu mewn dwy linell o fetadata a dim
byd arall — sylw marciwr sy'n ei adnabod fel neges llinyn-t, a rhif llinell
ffynhonnell:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Dim baner `fuzzy`, dim ailgyfieithu, mewn unrhyw iaith. Mae'r neges yn rendro ar
unwaith:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "Bydd `update --check` yn adrodd bod y catalogau'n hen ffasiwn"

    Mae'r sylw marciwr hwnnw a'r rhifau llinell a symudodd yn ddigon i
    `pybabel update --check` ddweud bod angen ailgynhyrchu catalog, am ei fod
    yn cymharu'r cofnod cyfan ac nid y cyfieithiad yn unig. Rhedwch y `pybabel
    update` go iawn yn yr un ymrwymiad â newid y cod, ac ymrwymwch y catalogau
    gydag ef — yr un arfer y mae'r [gât CI](workflow.md#what-ci-gates) eisoes yn
    gofyn amdano.

## O fformat-`%`: mae'r msgid yn newid, felly aiff cyfieithiadau'n fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Mae cystrawen printf yn byw *y tu mewn* i'r neges, felly mae ei disodli'n
ailysgrifennu allwedd y catalog. Nid oes ffordd o osgoi hynny, a dyna gost onest
gadael `%(name)s` ar ôl:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

Mae `pybabel update` yn adnabod y neges newydd fel perthynas agos i'r un a
dynnwyd ac yn cario'r hen gyfieithiad drosodd, wedi'i farcio'n fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Tri pheth i'w gwybod am y cyflwr hwnnw:

- **Nid oes dim yn torri wrth redeg.** Caiff cofnodion fuzzy eu heithrio o'r
  `.mo` wedi'i grynhoi, felly mae'r rhaglen yn rendro'r neges ffynhonnell hyd
  nes y bydd person yn cadarnhau'r pâr — [yr un diraddio](workflow.md#the-cycle-after-the-first-translation)
  y mae unrhyw neges a aildroswyd yn mynd drwyddo.
- **Mae CI yn aros yn wyrdd tra byddant yn fuzzy.** Mae'r gwiriwr dalwyr lle'n
  hepgor cofnodion fuzzy, yn union fel y mae `msgfmt --check-format` yn ei
  wneud, am na ddylai cofnod na all gyrraedd y rhedeg fethu adeiladwaith. Y
  foment y bydd cyfieithydd yn clirio'r faner, gwirir y cofnod fel unrhyw un
  arall — felly caiff `%(name)s` a adawyd mewn cyfieithiad cadarnhaol ei ddal
  bryd hynny, sef yr union bwynt y byddai fel arall yn dechrau rendro.
- **Mae'r hen faner `python-format` yn teithio gydag ef** a dylid ei dileu
  gyda'r faner `fuzzy`, neu bydd `msgfmt --check-format` yn dal i gymhwyso
  rheolau printf at neges fformat-braced.

Ar gyfer dalwyr lle printf wedi'u henwi mae'r golygu'n fecanyddol — daw
`%(name)s` yn `{name}` ac nid oes dim arall yn symud — felly mae catalog mawr yn
bas wedi'i sgriptio ac wedyn adolygiad cyfieithydd, yn hytrach nag ailgyfieithu.
Nid yw `%s` safleol yn fecanyddol: nid oes ganddo enw i'w gario drosodd, a
dewis un yw pwynt y newid.

Gall y mudo felly fynd yn ei flaen ar ba bynnag gyflymder y mae adolygu'n ei
ganiatáu: darn gweladwy o waith yn y catalog yw cofnod fuzzy heb ei drosi, nid
adeiladwaith toredig.

## Mae hen alwadau a rhai newydd yn cydfodoli { #old-and-new-calls-coexist }

Mae'r echdynnwr sy'n darllen llinynnau-t hefyd yn darllen galwadau gettext
cyffredin, felly mae un mapio'n ymdrin â ffeil sydd hanner ffordd drwy fudo:

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

Mae'r ddwy neges yn glanio yn yr un templed, a dim ond yr un llinyn-t sy'n cario
sylw'r marciwr sy'n troi gwirio ychwanegol y llyfrgell hon ymlaen:

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

Mae'n adnabod `_()`, y pedwar enw gettext safonol, yr enwau eraill `tr()` /
`ntr()`, a'r rhai gohiriedig `lazy_gettext()` / `lazy_pgettext()`. Rhaid
[enwi](extraction.md#registering-your-own-function-names) cynorthwyydd o'ch
eiddo chi yn y mapio.

Wrth redeg mae'r ddwy arddull yr un mor annibynnol: mae
`gettext.translation()` yn dychwelyd un gwrthrych cyfieithiadau, ac mae `_` a
phwyntiau mynediad y llyfrgell hon yn darllen ohono.

## Yr hyn nad yw'n symud { #what-does-not-move }

- **Ieithoedd templedu.** Mae `{% trans %}` Jinja2, tagiau templed Django, a'u
  hechdynwyr Babel yn dal i weithio'n ddigyfnewid ac yn dal i fwydo'r un
  catalogau PO. Cystrawen Python yw llinynnau-t; maent yn berthnasol i
  ffynhonnell Python.
- **Eich ffeiliau catalog.** Dim newid fformat, dim ffeil newydd, dim cam trosi.
- **Eich llwyfan cyfieithu.** Mae'r cyfnewid `.po` yn union yr un fath, ac mae'r
  faner `python-brace-format` y mae neges llinyn-t yn ei chario yr un faner ag y
  mae neges `.format()` yn ei chario — felly mae QA dalwyr lle'n dal i weithio.
- **Cod nad yw'n Python.** Nid effeithir ar gatalog JavaScript nac C yn yr un
  prosiect.

## Rhestr wirio fudo { #a-migration-checklist }

1. Ychwanegwch yr ychwanegyn `babel` lle mae `pybabel` yn rhedeg, a newidiwch y
   mapio `python` yn `babel.cfg` i'r dull `gettext_tstrings` — mae un mapio wedyn
   yn ymdrin â'r ddwy arddull, ac mae `-k` yn dal i weithio ar gyfer y galwadau
   cyffredin.
2. Trowch safleoedd galw `.format()` yn gyntaf. Ail-echdynnwch, rhedwch
   `pybabel update`, ac ymrwymwch y catalogau gyda'r cod; disgwyliwch ddim
   cofnodion fuzzy.
3. Trowch safleoedd galw fformat-`%` mewn sypiau y gallwch eu cael wedi'u
   hadolygu, gan ailysgrifennu'r dalwyr lle a gariwyd drosodd a chlirio'r
   baneri `fuzzy` a `python-format`.
4. Trwsiwch yr hyn y mae'r cyfyngiad yn ei wrthod: rhaid i ryngosodiad fod yn
   enw syml, felly daw `t"Hello {user.name}"` yn newidyn lleol yn gyntaf.
   Golygiad safle galw yw hwn, nid un catalog.
5. Trowch `strict = true` ymlaen ym mapio'r echdynnwr unwaith y bydd yr ysgubo
   ar ben, fel bod neges na ellir ei hechdynnu'n methu
   [yr adeiladwaith](extraction.md#lenient-locally-strict-in-ci) yn hytrach na
   diflannu o'r templed.
6. Ychwanegwch y gwiriad rhedeg o [Mewn cynhyrchu](workflow.md#what-ci-gates):
   rendrwch un neges fesul iaith a gludir drwy `Translator` llym.

Ymrwymiadau cyffredin yw camau 2 a 3. Nid oes dim yn y rhestr hon angen diwrnod
troi.
