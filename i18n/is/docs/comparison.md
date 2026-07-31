---
description: "Sömu þýðanlegu skilaboðin rituð með %-sniði, .format(), $-strengjum flufl.i18n og t-streng, ásamt því hvernig hvert bindur gildi og bregst við skemmdri þýðingaskrá."
---

# Hvers vegna t-strings

Fjórar leiðir til að koma gildi inn í þýðanleg skilaboð, bornar saman á sömu
setningunni. Stutta útgáfan:

- Með **%-sniði** verður einn stafur sem þýðandi eyðir að hruni í rekstri.
- Með **str.format** getur þýðing lesið eigindi af hlutunum sem kóðinn þinn
  réttir inn — leyndarmál þar með talin.
- Með **$-strengjum** (flufl.i18n) eru gildin sótt óbeint í breytur
  kallandi falls, og punktaðir staðgenglar ná líka í eigindi.
- Með **t-strengjum** helst sniðið í kóðanum þínum, þýðingar eru athugaðar á
  keyrslutíma, og biluð þýðingaskrá fellur aftur í frumtextann í stað þess
  að hrynja.

Afgangur þessarar síðu er sönnunargagnið, ein aðferð í einu.

!!! note "Þrír aðilar koma við hver þýdd skilaboð"

    **Þýðingaskrá** er skráin með þýðingunum — `.po` meðan fólk ritar hana,
    vistþýdd í `.mo` fyrir forritið að lesa inn ([kennsluefnið](tutorial.md)
    gengur gegnum hvort tveggja). Þrír aðilar koma við hver skilaboð:
    **forritarinn** skrifar frumstrenginn, **þýðandi** ritar þýðingaskrána —
    oft á utanaðkomandi vettvangi, langt frá öllum kóðayfirlestri — og
    **forritið** birtir þau tvö saman á keyrslutíma. Hver sniðstíll hér að
    neðan svarar sömu spurningunni á sinn hátt: *hversu miklu af sniðmálinu
    fær þýðingaskráin að stjórna?* Í dæmunum er `_` venjubundna nafnið á
    þýðingarfallinu og `tr` er nafnið í þessu safni.

## %-snið { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Hvað getur farið úrskeiðis: einn stafur sem er eytt úr þýðingu felldi
birtinguna.

Strengurinn í þýðingaskránni ber printf-málskipan, þar með talinn
tegundarstaf í enda — `s`-ið í `%(name)s` — sem er auðvelt að yfirsjást og
auðvelt að skemma:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Breyting á einum staf í PO-ritli verður að rakningu í rekstri. GNU
`msgfmt --check-format` grípur það vissulega, en aðeins fyrir skilaboð sem
eru merkt `python-format`, og aðeins ef þýðingaskráin fer raunverulega gegnum
msgfmt á leið sinni í forritið þitt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Það losar okkur við tegundarstafinn í endanum en heldur staðgengli sem hefur
nafn og má víxla frjálst. Það sem getur farið úrskeiðis færist yfir á hina
hlið viðskiptanna: þýðingin fær vald yfir hlutunum þínum.

`str.format` er lítið segðamál, og að kalla á það á streng þýðir að rétta
þeim streng réttinn til að nota það:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Settu nú hvað sem `_()` skilar í stað þessara föstu strengja. Ef þýðing á
`Hello {name}` kemur til baka sem `{conf.api_key}`, þá prentar birting hennar
API-lykilinn þinn — þýðingaskráin, ekki kóðinn þinn, réð því hvað var lesið.
Þýðingaskrá er ekki kóði, en hún ferðast eins og gögn: út á þýðingavettvang,
gegnum margar hendur, til baka sem `.po`, vistþýdd í `.mo`, stundum fengin
að láni algjörlega utan verkefnisins þíns. `.format()` gefur hverju skrefi
þeirrar ferðar aðgang að eigindum hlutanna sem þú réttir inn.

## `$`-strengir og flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] úr staðalsafninu leggur til
innskeytingarmálið `$name`, en er ekki sjálft þýðingar-API.
[`flufl.i18n`][flufl-i18n] sameinar þann stíl við uppflettingu í
gettext-þýðingaskrá. Taktu eftir að gildið er aldrei rétt inn: flufl.i18n
byggir nafnrými útskiptinganna úr altækum og staðværum breytum kallandans —
hvaða breytur sem eru til á kallstaðnum standa skilaboðunum til boða.
Valfrjáls `extras`-vörpun gengur framar hvoru tveggja. Málskipanin sem
þýðandinn sér hefur hvorki tegundarstaf í enda né sniðlýsingu, og staðgengla
má áfram víxla frjálst.

Útskipting sem ekki er til varpar engu. Með `name = "Ada"` og engan `nombre`
í nafnrými kallandans birtist þýðing þýðingaskrárinnar á `Hello $nombre` sem
`Hello $nombre`: óleysti staðgengillinn stendur eftir sýnilegur. Sú
[skjalfesta hegðun][documented behavior] varðveitir afganginn af þýddu
skilaboðunum í stað þess að fella kallið. Frávörp sem verpast við að leysa
eigindi eða umbreyta gildi geta þó enn borist upp.

`flufl.i18n` getur meira en ber `string.Template` á einn hátt sem skiptir
máli hér. Hið [sérsniðna Template][custom Template] tekur við punktuðum
staðgenglum á borð við `$settings.api_key`, og [þýðandinn][translator] leysir
þær slóðir upp gagnvart gildum kallandans. Þýddur staðgengill má nefna hvaða
staðværu eða altæku breytu kallandans sem er og, með punktaðri ritmynd,
ferðast um eigindi hennar. Það er þægilegt þegar skilaboð þurfa á eigindi að
halda, en gerir um leið ramma kallandans að hluta af nafnrými útskiptinganna
í þýðingaskránni. Samanburðurinn hér að neðan lýsir `flufl.i18n` 6.0.0, ekki
hverri mögulegri notkun á `string.Template`.

Það svarar líka spurningu sem hinir tveir sniðstílarnir skilja alfarið eftir
hjá forritinu: *hvaða* tungumál er virkt, og hvernig því er skipt.
[Forritshlutur][application object] heldur utan um stafla af tungumálum,
`_.push(code)` og `_.pop()` hreyfa hann, `with _.using(code):` má hreiðra, og
[stefna][strategy] finnur þýðingaskrána fyrir tiltekinn tungumálakóða, svo að
forritið handleiki aldrei sjálft hluti með þýðingaskrám. Þjónn sem þarf að
framleiða texta á fleiri en einu tungumáli innan sömu vinnueiningar — síðu
fyrir lesandann, tilkynningu til einhvers sem hefur annað tungumál stillt — er
einmitt tilvikið sem þetta er til fyrir.

Staflinn býr á þessum forritshlut, sem allt ferlið deilir. Tvær beiðnir sem
skarast deila því einum stafla, og blokkir sem eru ekki stranglega hreiðraðar
*í tíma* rétta hvor annarri rangt tungumál:

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

Þetta safn heldur sömu getunni — bindingar hreiðrast og rakna upp á sama hátt
— en geymir hana í `ContextVar` í stað sameiginlegs stafla, svo að fléttan hér
að ofan leysist fyrir hvert verk um sig. Samsvarandi dæmi eru á
[Mörg tungumál í einu](guide.md#several-languages-at-once). Það sem safnið
leggur ekki til er uppflettingin úr tungumálakóða í þýðingaskrá: þú réttir inn
hlut með þýðingunum, sem í venjulega tilvikinu er eitt kall á
`gettext.translation()`, og staðalsafnið heldur þáttuðu þýðingaskránni í
skyndiminni.

## t-strengir { #t-strings }

```python
tr(t"Hello {name}")
```

Þýðingaskráin sér áfram `Hello {name}` og er áfram venjuleg PO/MO-skrá.
Munurinn liggur í því hvað þýðing *má segja*, og hver athugar það.

Þetta safn athugar hverja þýðingu gagnvart staðgenglum frumskilaboðanna áður
en það birtir hana, og það tekur við berum nöfnum og engu öðru. Gagnvart
`t"Hello {name}"`:

| Þýðing sem inniheldur | er hafnað með |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Hafnað þýðir ekki hrunið: sjálfgefið skráir safnið viðvörun og birtir
frumtextann, svo að léleg þýðingaskrá fellir aldrei forritið —
[sami samningur og gettext sjálft heldur](guide.md#what-happens-when-a-catalog-is-wrong).

Sniðið helst þar sem það var skrifað, í kóðanum:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` kemst aldrei í þýðingaskrána, svo engin þýðing getur breytt því og
enginn þýðandi þarf að líta á það.

Enn einn munurinn er tólastuðningur: t-strengir eru ný málskipan, svo að
draga þá út í `.pot` krefst sem stendur útdráttartóls sem kann á t-strengi,
eins og þess sem þessi pakki [leggur til fyrir Babel](extraction.md).

## Hlið við hlið { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Hefur staðgengillinn nafn? | já | já | já | já |
| Má þýðandi víxla staðgenglum til? | já | já | já | já |
| Hvaðan koma gildin? | úr skýrri vörpun | úr skýrum viðföngum | úr staðværum og altækum breytum kallandans, auk valfrjálsra `extras` | úr gildunum sem gripin voru inni í t-strengnum |
| Getur þýðingaskráin breytt því hvernig gildi er sniðið? | já | já | nei | nei |
| Getur þýðingaskráin teygt sig inn í hluti (aðgangur að eigindum)? | nei | já | já, með punktuðum nöfnum | nei |
| Þýðing *sleppir* staðgengli — hvað birtist? | gildið hverfur hljóðlaust | gildið hverfur hljóðlaust | gildið hverfur hljóðlaust | frumtextinn, með viðvörun ([sjálfgefið](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Þýðing *bætir við* óþekktum staðgengli — hvað birtist? | frávarp | frávarp | staðgengillinn stendur eftir sýnilegur sem texti | frumtextinn, með viðvörun ([sjálfgefið](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Eru staðgenglar athugaðir við birtingu? | nei | nei | nei | já (sjá hér að neðan) |
| Hvaða PO-flagg leiðir Babel út, svo að tól sem fyrir eru geti staðfest? | `python-format` | `python-brace-format` | ekkert | `python-brace-format` |
| Notar venjulegar PO/MO-þýðingaskrár? | já | já | já | já |
| Þarf sérstakt útdráttartól fyrir frumkóðann? | nei | nei | nei | já, sem stendur |
| Hvar býr „núverandi tungumál“? | þar sem forritið kýs að setja það | þar sem forritið kýs að setja það | stafli af tungumálakóðum á sameiginlega forritshlutnum | `ContextVar`, eitt fyrir hvert verk eða hverja beiðni |

Um athugunina við birtingu: eintöluskilaboð eru athuguð með nákvæmri
samsvörun staðgengla. Fleirtöluskilaboð eru líka athuguð, gagnvart
[sammengis-/sniðmengisreglunni](spec.md) sem leyfir fleirtölumyndum
markmálsins að vera aðrar en frummálsins; strangari athugunin á hverja mynd
keyrir þegar þýðingaskrár eru vistþýddar ([Útdráttur](extraction.md)).

Línan um sniðflaggið snýst um athugun sem kann á staðgengla, ekki um
samhæfni þýðingaskráa. `ekkert` þýðir að stöðluð gettext-tól lesa og
vistþýða skilaboðin eftir sem áður, en `msgfmt --check-format` hefur enga
málfræði fyrir `$`-staðgengla til að beita.

## Hvað það kostar { #what-it-costs }

f-streng er alls ekki hægt að nota svona — um leið og nokkurt safn sér hann
er hann þegar fullgerður strengur, svo að þýða hann þýðir að þýða brot.
t-strengir ([PEP 750]) halda föstum textanum og gildunum aðskildum en halda
um leið málskipan sem líkist f-strengjum og skýrri bindingu gilda.
`$`-strengir bjóða þegar upp á hnitmiðaðan valkost með annars konar
bindingu og annars konar líkani af bilunum. `flufl.i18n` er þroskaður pakki
sem keyrir á Python 3.10 og síðar; `gettext-tstrings` er sem stendur
alfa-útgáfa, og af því að t-strengir eru ný málskipan krefst hann Python
3.14 eða nýrri.

Hinn kostnaðurinn er takmörkunin sjálf: innskeyting verður að vera bert nafn.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Það er raunveruleg hömlun. Ásamt bindingu gilda á hlið frumtextans og
athugun staðgengla á keyrslutíma kemur hún í veg fyrir að strengir í
þýðingaskrá reikni út segðir, og heldur nöfnum staðgengla merkingarbærum.

Hvernig Python rataði á þessi vegamót — tveir PEP-ar með tíu ára millibili,
og umræðan í staðalsafninu sem lokaðist án svars — er sagt með heimildum á
[Bakgrunnur](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
