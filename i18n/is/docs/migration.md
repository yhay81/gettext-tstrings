---
description: "Að taka upp t-strengi í verkefni sem hefur nú þegar gettext-þýðingaskrár: hvað lifir ósnert af, hvað verður óskýrt og hvernig á að færa einn köllunarstað í einu."
---

# Yfirfærsla

Noti verkefnið þitt nú þegar gettext eru spurningarnar sem ráða því hvort
þetta safn sé nothæft þröngar: ógildir það þýðingaskrárnar sem þú átt, getur
það lifað hlið við hlið með kóðanum sem þú ert ekki tilbúin að breyta, og hve
mikið af færslunni verður að gerast í einu. Svörin, þau stystu fyrst:

| Spurning | Svar |
| --- | --- |
| Virka núverandi `.po`- og `.mo`-skrár áfram? | Já. Sömu skrár, sömu tól. |
| Geta gömul og ný köll búið í einni skrá? | Já, og ein útdráttarvörpun nær yfir bæði. |
| Breytist msgid? | Ekki frá `.format()`. Já frá `%`-sniði. |
| Verður allt verkefnið að færast í einu? | Nei. Einn köllunarstaður er gild breyting. |
| Hvað um Jinja, Django-sniðmát, JavaScript? | Ósnert, sömu þýðingaskrár. |

Afgangur þessarar síðu er smáatriðin á bak við hvert þessara.

## Frá `.format()`: msgid breytist ekki { #from-format-the-msgid-does-not-change }

Þetta er tilvikið þar sem yfirfærslan kostar nánast ekkert. Skilaboð með
`str.format` og skilaboð með t-streng leiða út *sama* þýðingaskrárlykil, því
lykillinn er textinn með `{name}` inni í honum hvor leiðin sem farin er:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Þannig helst núverandi þýðing áföst. Út frá þýðingaskrá sem geymir

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

skaltu breyta kallinu, draga út á ný og uppfæra:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Færslan sem kemur til baka er frábrugðin í tveimur línum lýsigagna og engu
öðru — athugasemdarmerki sem auðkennir hana sem t-strengsskilaboð, og
línunúmer í frumkóða:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Enginn `fuzzy`-fáni, engin endurþýðing, í neinu tungumáli. Skilaboðin birtast
strax:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` mun tilkynna þýðingaskrárnar sem úreltar"

    Þetta athugasemdarmerki og færðu línunúmerin nægja til þess að
    `pybabel update --check` segi að þýðingaskrá þurfi að endurgera, því það
    ber saman alla færsluna en ekki þýðinguna eina. Keyrðu raunverulegt
    `pybabel update` í sömu framlagningu og kóðabreytinguna og framlagðu
    þýðingaskrárnar með henni — sami vaninn og
    [CI-hliðið](workflow.md#what-ci-gates) biður nú þegar um.

## Frá `%`-sniði: msgid breytist, svo þýðingar verða óskýrar { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf-málskipan býr *inni í* skilaboðunum, svo að skipta henni út umskrifar
þýðingaskrárlykilinn. Það er engin leið framhjá því og það er heiðarlegur
kostnaður þess að skilja `%(name)s` eftir:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` þekkir nýju skilaboðin sem náinn ættingja þeirra sem
fjarlægð voru og flytur gömlu þýðinguna yfir, merkta óskýra:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Þrennt er vert að vita um það ástand:

- **Ekkert brotnar á keyrslutíma.** Óskýrar færslur eru útilokaðar frá
  vistþýddu `.mo`-skránni, svo forritið birtir frumtextann þar til manneskja
  staðfestir parið — [sama hnignunin](workflow.md#the-cycle-after-the-first-translation)
  og hver endurorðuð skilaboð ganga gegnum.
- **CI helst grænt meðan þær eru óskýrar.** Staðgengilsathugunin sleppir
  óskýrum færslum, nákvæmlega eins og `msgfmt --check-format` gerir, því
  færsla sem kemst ekki á keyrslutímann á ekki að fella byggingu. Um leið og
  þýðandi hreinsar fánann er færslan athuguð eins og hver önnur — svo
  `%(name)s` sem skilið er eftir í staðfestri þýðingu grípst þá, sem er
  einmitt sá punktur þar sem það myndi annars fara að birtast.
- **Gamli `python-format`-fáninn flýtur með** og á að eyða ásamt
  `fuzzy`-fánanum, ella heldur `msgfmt --check-format` áfram að beita
  printf-reglum á skilaboð með slaufusvigasniði.

Fyrir nefnda printf-staðgengla er breytingin vélræn — `%(name)s` verður
`{name}` og ekkert annað hreyfist — svo stór þýðingaskrá er skriftuð yfirferð
og síðan yfirlestur þýðanda, fremur en endurþýðing. Staðsetningarbundið `%s`
er ekki vélrænt: það hefur ekkert nafn til að flytja yfir, og að velja það er
allur tilgangur breytingarinnar.

Yfirfærslan getur því gengið á þeim hraða sem yfirlestur leyfir: óumbreytt
óskýr færsla er sýnilegt verk í þýðingaskránni, ekki biluð bygging.

## Gömul og ný köll lifa hlið við hlið { #old-and-new-calls-coexist }

Útdráttarforritið sem les t-strengi les einnig venjuleg gettext-köll, svo ein
vörpun nær yfir skrá í miðri yfirfærslu:

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

Bæði skilaboðin lenda í sama sniðmátinu og aðeins t-strengsskilaboðin bera
athugasemdarmerkið sem kveikir á aukaathugun þessa safns:

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

Það þekkir `_()`, fjögur stöðluð gettext-nöfn, samheitin `tr()` / `ntr()`, og
frestuðu `lazy_gettext()` / `lazy_pgettext()`. Hjálparfall sem þú skrifar
sjálf verður að vera [nefnt í vörpuninni](extraction.md#registering-your-own-function-names).

Á keyrslutíma eru stílarnir tveir jafn óháðir: `gettext.translation()` skilar
einum þýðingahlut og bæði `_` og aðgangsstaðir þessa safns lesa úr honum.

## Hvað færist ekki { #what-does-not-move }

- **Sniðmátsmál.** `{% trans %}` í Jinja2, sniðmátsmerki Django og
  Babel-útdráttarforrit þeirra halda áfram að virka óbreytt og halda áfram að
  fæða sömu PO-þýðingaskrárnar. T-strengir eru Python-málskipan; þeir eiga við
  um Python-frumkóða.
- **Þýðingaskrárnar þínar.** Engin sniðbreyting, engin ný skrá, ekkert
  umbreytingarskref.
- **Þýðingavettvangurinn þinn.** `.po`-skiptin eru eins, og
  `python-brace-format`-fáninn sem t-strengsskilaboð bera er sami fáni og
  `.format()`-skilaboð bera — svo staðgengilsgæðaeftirlit heldur áfram að
  virka.
- **Kóði sem er ekki Python.** JavaScript- eða C-þýðingaskrá í sama verkefni
  verður ekki fyrir áhrifum.

## Gátlisti fyrir yfirfærslu { #a-migration-checklist }

1. Bættu `babel`-viðbótinni við þar sem `pybabel` keyrir og breyttu
   `python`-vörpuninni í `babel.cfg` yfir í `gettext_tstrings`-aðferðina — ein
   vörpun nær þá yfir báða stílana og `-k` heldur áfram að virka fyrir
   venjulegu köllin.
2. Umbreyttu `.format()`-köllunarstöðum fyrst. Dragðu út á ný, keyrðu
   `pybabel update` og framlagðu þýðingaskrárnar með kóðanum; búastu ekki við
   neinum óskýrum færslum.
3. Umbreyttu `%`-sniðs köllunarstöðum í lotum sem þú getur fengið yfirlesnar,
   umskrifaðu staðgenglana sem fluttust yfir og hreinsaðu `fuzzy`- og
   `python-format`-fánana.
4. Lagaðu það sem takmörkunin hafnar: innskot verður að vera einfalt nafn, svo
   `t"Hello {user.name}"` verður fyrst að staðværri breytu. Þetta er breyting
   á köllunarstað, ekki á þýðingaskrá.
5. Kveiktu á `strict = true` í útdráttarvörpuninni þegar yfirferðinni er
   lokið, svo að skilaboð sem ekki er hægt að draga út felli
   [bygginguna](extraction.md#lenient-locally-strict-in-ci) fremur en að hverfa
   úr sniðmátinu.
6. Bættu við keyrslutímaathuguninni úr [Í rekstri](workflow.md#what-ci-gates):
   birtu ein skilaboð fyrir hvert útgefið tungumál gegnum strangan
   `Translator`.

Skref 2 og 3 eru venjulegar framlagningar. Ekkert á þessum lista þarfnast
umskiptadags.
