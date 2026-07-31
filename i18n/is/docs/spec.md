---
description: "Venjan frá t-streng til msgid sem lítill útgáfumerktur samningur, með vélleseinlegum samræmisprófum."
---

# Forskrift

Þú getur notað þetta safn án þess að lesa þessa síðu —
[kennsluefnið](tutorial.md) og [handbókin](guide.md) ná yfir daglega notkun.
Þessi síða er fyrir höfunda tóla: venjan sem safnið útfærir er skrifuð niður
sem lítill, stöðugur samningur svo að önnur útfærsla — útdráttartól,
þróunarumhverfi, tegundayfirfari eða `pygettext` framtíðarinnar — geti miðað
við hana og unnið með henni. Fyrir sömu reglurnar útskýrðar með ástæðum
sínum, og hvernig viðmiðunarútfærslan framkvæmir þær, lestu fyrst
[Hvernig þetta virkar](internals.md).

[Lesa forskrift v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Reglurnar á einum skjá { #the-rules-in-one-screen }

**Msgid** er samskeyting, í röð frumtextans, á föstu bútunum og einu
`{name}`-tákni fyrir hverja innskeytingu. Slaufusvigar sem eiga að standa
sem stafir eru escape-ritaðir (`{` verður `{{`). Nafn verður að vera einfalt
staðgengilsnafn — `str.isidentifier()` er satt og það er ekki lykilorð í
Python. Umbreytingar og sniðlýsingar eru **ekki** hluti af msgid-inu; þær
haldast undir stjórn forritsins.

| t-strengur | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *hafnað — ekki einfalt nafn* |

**Þýðing** er gild þegar hún inniheldur eingöngu bera `{name}`-staðgengla,
hvert áskilið nafn kemur að minnsta kosti einu sinni fyrir, og ekkert nafn
utan leyfða mengisins birtist. Víxlun og endurtekning eru af ásettu ráði
óheftar: hvort tveggja getur verið málfræðilega nauðsynlegt í markmáli.

Fyrir fleirtölu er *leyfilegt* sammengi nafnanna í greinunum og *áskilið*
sniðmengi þeirra — svo að `t"One file"` andspænis `t"{n} files"` gerir `n`
aðgengilegt þeim sem þýðir hvora mynd sem er en áskilur hann í hvorugri, og
fleirtölureglur markmálsins mega vera aðrar en frummálsins.

**Tómt msgid** er aldrei flett upp, því gettext tekur það frá fyrir
lýsigagnahaus þýðingaskrárinnar.

## Samræmi { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
er sama skjalið á vélleseinlegu formi: tilvik sem varpa fastri byggingu
t-strengs yfir í msgid, og msgid ásamt mynstri þýðingaskrár yfir í birtan
streng eða höfnun.

Útfærsla **samræmist forskrift v1** þegar hún endurgerir hvert einasta
tilvik. Tilvikin nefna aðeins það sem forskriftin skilgreinir — leidd
msgid, samþykkt og hafnað mynstur, birt úttak — og aldrei villuboð eða
tegund frávarps, svo að útfærsla í öðru forritunarmáli getur keyrt þau
óbreytt.

Innskeytingum er lýst eftir byggingu, aldrei sem Python-frumkóða:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Viðmiðunarútfærslan keyrir prófmengið sem hluta af sínu eigin prófmengi,
svo að textinn og kóðinn geta ekki rekið hljóðlaust í sundur.

## Útgáfunúmer { #versioning }

Þetta er forskrift v1. Breyting sem er ekki afturvirkt samhæf á leiðslu
msgid-a eða á athugun þýðinga hækkar útgáfunúmerið og lætur nýja
`conformance/vN.json` fylgja við hlið þeirrar sem fyrir er. Viðbætur til
skýringar sem breyta hvorki leiddum msgid-um né samþykktum mynstrum gera
það ekki.
