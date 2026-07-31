---
description: "Þrjátíu ár af gettext, tveir PEP-ar með tíu ára millibili og umræðan í staðalsafninu sem lokaðist sem ekki-fyrirhuguð: hvers vegna þetta safn er til, með tenglum í heimildir."
---

# Bakgrunnur

Þetta safn stendur þar sem tvær langar sögur mætast — önnur um það hvernig
hugbúnaður er þýddur, hin um það hvernig Python skeytir gildum inn í strengi
— sögur sem skárust loks árið 2025 og stöðvuðust svo einmitt á þeim punkti
þar sem þörf var á lítilli, vandaðri venju. Þessi síða segir báðar sögurnar,
með tenglum í heimildir, því hönnunarákvarðanirnar á þessum vef er auðveldara
að meta þegar maður sér spurningarnar sem þær svara.

## Vistkerfi gettext { #the-gettext-ecosystem }

[GNU gettext] hefur verið leiðin til að þýða frjálsan hugbúnað síðan um
miðjan tíunda áratuginn: merktu strengina í kóðanum, dragðu þá út í sniðmát,
gefðu þýðendum eina þýðingaskrá fyrir hvert tungumál, vistþýddu, lestu inn á
keyrslutíma. Utan um þá hringrás óx heilt vistkerfi — PO-ritlar,
yfirlestrarferli og þýðingavettvangar sem tala allir sama skráarsniðið — og
Python hefur haft [`gettext`-eininguna][stdlib-gettext] í staðalsafni sínu í
meira en tvo áratugi. Keyrslutímahelmingur þýðinganna var aldrei vandinn.

Óútkljáði helmingurinn var alltaf *hvernig strengurinn í þýðingaskránni
lítur út*. Skilaboð með `%(name)s` rétta þýðendum printf-málskipan sem einn
stafur sem eytt er breytir í hrun í rekstri; skilaboð með `.format()` rétta
þýðingaskránni aðgang að eigindum lifandi hluta.
([Hvers vegna t-strings](comparison.md) gengur gegnum hvort tveggja, með
bilanirnar til sýnis.) Og f-strengir — málskipanin sem mestur Python-kóði
kýs nú — geta alls ekki tekið þátt: um leið og nokkurt safn sér einn slíkan
er hann þegar fullgerður strengur. Fólk reynir samt, nógu oft til þess að
verkefnaskrá Babel safnar tilraununum ([#594][babel-594], [#715][babel-715]);
bilunin er byggingarleg, ekki eiginleiki sem vantar.

## Tveir PEP-ar með tíu ára millibili { #two-peps-ten-years-apart }

Árið 2015 skrifuðu Alyssa Coghlan og Nick Humrich [PEP 501], sem lagði til
innskeytingarsniðmát og nefndi i18n sem sína fyrstu hvöt — "providing a
cleaner syntax for i18n translation", með orðum PEP-sins sjálfs. Tillögunni
var frestað, meðal annars af því að umræðan sýndi að i18n-tilvikið bar með
sér umtalsverð aukaatriði sem einfaldari notkunartilvik báru ekki.

Áratug síðar vakti [PEP 750] — eftir Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou og Dave Peck — hugmyndina aftur til
lífsins sem t-strengi, var [samþykktur í apríl 2025][sc-resolution] og kom út
í [Python 3.14] í október 2025. PEP 501 var þá dreginn til baka honum í vil.
Eitt atriði skiptir máli fyrir þessa síðu: i18n er *ekki* meðal þeirra hvata
sem PEP 750 nefnir. PEP-inn alhæfði vélbúnaðinn — sniðmátstegund sem hvaða
safn sem er getur nýtt — og skildi þýðingarspurninguna eftir nákvæmlega þar
sem PEP 501 hafði lagt hana tíu árum fyrr: opna.

Þannig að frá og með Python 3.14 hafði málið nákvæmlega þá gagnabyggingu sem
skilaboðaskrá þarf, og enga venju um að nota hana sem slíka.

## Umræðan í staðalsafninu { #the-stdlib-discussion }

Tveimur mánuðum áður en 3.14 kom út lagði Adrian Mönnich (ThiefMaster, einn
umsjónarmanna Indico-verkefnisins) til að fylla þetta gat í staðalsafninu
sjálfu: þráðurinn [Support t-strings in gettext][discuss-thread] á
discuss.python.org, opnaður í ágúst 2025, kom með virkri
[breytingabeiðni][cpython-pr] sem bætti stuðningi við t-strengi í bæði
`gettext` og `pygettext`.

Þráðurinn er þess virði að lesa í heild sinni, því hann dregur fram hverja þá
erfiðu spurningu sem þetta safn þurfti síðar að svara:

- **Hvað má innskeyting vera?** Aðeins einfalt nafn, eða eigindi og köll með
  leiddu staðgengilsnafni? Sérhvert svar skiptir á þægindum og stöðugleika
  msgid-a og öryggi þýðingaskrár.
- **Hvers krefjast fleirtölumyndir,** þegar fleirtölukerfi markmálsins er
  annað en frummálsins?
- **Er gettext yfirleitt rétta skotmarkið?** Barry Warsaw — sem hafði haldið
  því fram meðan PEP 750 var í smíðum að t-strengir hentuðu i18n illa —
  benti á [`flufl.i18n`][flufl-i18n] sitt og `$`-strengjastílinn sem
  vinsamlegra tólið; aðrir töluðu fyrir því að skilja gettext eftir
  algjörlega og taka upp nýrri kerfi á borð við [Fluent].
- **Og yfirspurningin:** hverju sem staðalsafnið sendir frá sér er nánast
  aldrei hægt að breyta. Venja með svona mörgum opnum valkostum er áhættusamt
  að festa í fyrstu atrennu.

Engin samstaða myndaðist. CPython-málinu var
[lokað sem „not planned“][cpython-issue] og breytingabeiðninni var lokað
ósamrunninni í október 2025, fáeinum dögum eftir útgáfu 3.14. Getan var til í
málinu; venjan átti sér ekkert heimili.

## Hvers vegna pakki, fyrst { #why-a-package-first }

Þetta er gatið sem þetta verkefni kaus að fylla utan staðalsafnsins, á
meðvituðu veðmáli: venja þroskast hraðar þar sem hún getur skipt um útgáfu
frjálst og unnið sér traust eitt tilvik í einu, og staðalsafnið — sem verður
að hafa rétt fyrir sér í fyrstu tilraun — er þar sem venja á að *enda*, ekki
þar sem hún á að verða til.

Nánar tiltekið á sérhver umdeild spurning í þræðinum skrifað svar hér, hvert
á sinni síðu:

- Innskeytingar eru **eingöngu einföld nöfn**, svo að msgid haldist stöðug og
  merkingarbær — [handbókin](guide.md#safety-and-scope) sýnir regluna,
  [Hvernig þetta virkar](internals.md#from-template-to-msgid) ástæðurnar.
- **Sniðið helst algjörlega utan þýðingaskrárinnar**
  ([Hvers vegna t-strings](comparison.md)).
- **Fleirtala** fylgir sammengis-/sniðmengisreglu sem leyfir fleirtölukerfi
  markmálsins að vera annað en frummálsins ([forskrift §4](spec.md)).
- Biluð þýðingaskrá **fellur til baka í stað þess að hrynja**, og heldur þar
  með samningi gettext sjálfs
  ([handbókin](guide.md#what-happens-when-a-catalog-is-wrong)).
- Og öll venjan er [útgáfumerkt forskrift](spec.md) með vélleseinlegum
  samræmisprófum — skrifuð þannig að önnur útfærsla, þar á meðal útfærsla í
  staðalsafninu í framtíðinni, gæti tekið hana upp óbreytta og unnið með
  henni.

Umræðunni er ekki lokið, og þetta verkefni er þátttakandi í henni, ekki
dómur um hana. Ef þú býrð að reynslu af gettext í rekstri sem varðar þessi
val, þá eru [sami þráður][discuss-thread] og
[Discussions][gh-discussions] þessarar geymslu staðirnir þar sem um það er
deilt.

## Tímalína { #timeline }

| Hvenær | Hvað gerðist |
| --- | --- |
| um miðjan 10. áratuginn | GNU gettext festir í sessi PO/POT/MO-hringrásina sem þýðendur og vettvangar tala enn. |
| 2015 | [PEP 501] leggur til innskeytingarsniðmát, með i18n sem fyrstu hvöt; frestað. |
| 2016 | f-strengir koma út í Python 3.6 — innskeyting fær sína málskipan, og þýðingar geta ekki notað hana. |
| júl. 2024 | [PEP 750] leggur til t-strengi. |
| apr. 2025 | PEP 750 [samþykktur][sc-resolution]; PEP 501 dreginn til baka honum í vil. |
| ágú. 2025 | Þráðurinn [Support t-strings in gettext][discuss-thread] opnast, með [breytingabeiðni][cpython-pr] í staðalsafnið. |
| okt. 2025 | [Python 3.14] kemur út með t-strengi; máli staðalsafnsins lokað sem [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` kemur út sem alfa, með [forskrift v1](spec.md) og samræmisprófum sínum. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
