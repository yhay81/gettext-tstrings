---
description: "Dertig jaar gettext, twee PEP's met tien jaar ertussen, en de stdlib-discussie die als not-planned gesloten werd: waarom deze bibliotheek bestaat, met links naar de bronnen."
---

# Achtergrond

Deze bibliotheek staat op het snijpunt van twee lange verhalen — één over hoe
software vertaald wordt, één over hoe Python strings interpoleert — die
elkaar in 2025 eindelijk kruisten en toen vastliepen op precies het punt waar
een kleine, zorgvuldige conventie nodig was. Deze pagina vertelt beide
verhalen, met links naar de bronnen, omdat de ontwerpbeslissingen op deze
site makkelijker te beoordelen zijn wanneer je de vragen kunt zien die ze
beantwoorden.

## Het gettext-ecosysteem { #the-gettext-ecosystem }

[GNU gettext] is sinds het midden van de jaren negentig de manier waarop
vrije software vertaald wordt: markeer de strings in code, extraheer ze naar
een sjabloon, geef vertalers één catalogusbestand per taal, compileer, laad
tijdens runtime. Rond die lus groeide een heel ecosysteem — PO-editors,
reviewworkflows en vertaalplatforms die allemaal hetzelfde bestandsformaat
spreken — en Python levert al meer dan twee decennia een
[`gettext`-module][stdlib-gettext] in zijn standaardbibliotheek. De
runtime-helft van vertalen was nooit het probleem.

De onopgeloste helft was altijd *hoe de catalogusstring eruitziet*. Een
`%(name)s`-bericht geeft vertalers printf-syntaxis die één verwijderde
letter in een productiecrash verandert; een `.format()`-bericht geeft de
catalogus attribuuttoegang tot levende objecten.
([Waarom t-strings](comparison.md) doorloopt beide, met de fouten in beeld.)
En f-strings — de syntaxis die de meeste Python-code nu verkiest — kunnen
helemaal niet meedoen: tegen de tijd dat een bibliotheek er een ziet, is het
al een afgeronde string. Mensen proberen het toch, vaak genoeg dat Babels
issue-tracker de pogingen verzamelt ([#594][babel-594], [#715][babel-715]);
het falen is structureel, geen ontbrekende feature.

## Twee PEP's, tien jaar uit elkaar { #two-peps-ten-years-apart }

In 2015 schreven Alyssa Coghlan en Nick Humrich [PEP 501], een voorstel voor
interpolatiesjablonen waarvan de eerstgenoemde motivatie i18n was —
"providing a cleaner syntax for i18n translation", in de woorden van de PEP
zelf. Het voorstel werd uitgesteld, deels omdat de discussie liet zien dat
het i18n-geval aanzienlijke extra overwegingen met zich meebracht die
eenvoudigere toepassingen niet hadden.

Een decennium later blies [PEP 750] — van Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou en Dave Peck — het idee nieuw leven
in als t-strings, werd het [geaccepteerd in april 2025][sc-resolution], en
verscheen het in [Python 3.14] in oktober 2025. PEP 501 werd daarop in zijn
voordeel ingetrokken. Eén detail is voor deze pagina van belang: i18n staat
*niet* onder de genoemde motivaties van PEP 750. De PEP generaliseerde het
mechanisme — een template-type dat elke bibliotheek kan consumeren — en liet
de vertaalvraag exact waar PEP 501 haar tien jaar eerder had geparkeerd:
open.

Dus vanaf Python 3.14 had de taal precies de datastructuur die een
berichtencatalogus nodig heeft, en geen conventie om haar als zodanig te
gebruiken.

## De stdlib-discussie { #the-stdlib-discussion }

Twee maanden voordat 3.14 uitkwam, stelde Adrian Mönnich (ThiefMaster, een
maintainer van het Indico-project) voor dat gat in de standaardbibliotheek
zelf te dichten: de thread [Support t-strings in gettext][discuss-thread] op
discuss.python.org, geopend in augustus 2025, kwam met een werkende
[pull request][cpython-pr] die t-string-ondersteuning toevoegde aan zowel
`gettext` als `pygettext`.

De thread is het waard om volledig te lezen, omdat hij elke moeilijke vraag
naar boven haalt die deze bibliotheek later moest beantwoorden:

- **Wat mag een interpolatie zijn?** Alleen een eenvoudige naam, of ook
  attributen en aanroepen met een afgeleide placeholdernaam? Elk antwoord
  ruilt gemak tegen msgid-stabiliteit en catalogusveiligheid.
- **Wat vereisen meervoudsvormen,** wanneer het meervoudssysteem van de
  doeltaal afwijkt van dat van de bron?
- **Is gettext überhaupt het juiste doel?** Barry Warsaw — die tijdens de
  ontwikkeling van PEP 750 had betoogd dat t-strings geen goede match voor
  i18n waren — wees naar zijn [`flufl.i18n`][flufl-i18n] en zijn
  `$`-string-stijl als het vriendelijkere gereedschap; anderen pleitten
  ervoor gettext helemaal achter te laten ten gunste van nieuwere systemen
  zoals [Fluent].
- **En de meta-vraag:** wat de standaardbibliotheek ook uitbrengt, het kan
  in wezen nooit meer veranderen. Een conventie met zoveel open keuzes is
  riskant om bij de eerste poging te bevriezen.

Er vormde zich geen consensus. Het CPython-issue werd
[gesloten als "not planned"][cpython-issue] en de pull request werd
ongemerged gesloten in oktober 2025, dagen na de release van 3.14. De
capaciteit bestond in de taal; de conventie had geen thuis.

## Waarom eerst een pakket { #why-a-package-first }

Dat is het gat dat dit project koos te vullen van buiten de
standaardbibliotheek, op een bewuste weddenschap: een conventie rijpt
sneller waar ze vrij kan versioneren en adoptie geval voor geval kan
verdienen, en de standaardbibliotheek — die het de eerste keer goed moet
hebben — is waar een conventie moet *eindigen*, niet waar ze moet worden
uitgewerkt.

Concreet heeft elke omstreden vraag uit de thread hier een opgeschreven
antwoord, elk op zijn eigen pagina:

- Interpolaties zijn **alleen eenvoudige namen**, zodat msgids stabiel en
  betekenisvol blijven — [de handleiding](guide.md#safety-and-scope) toont
  de regel, [Hoe het werkt](internals.md#from-template-to-msgid) de redenen.
- **Opmaak blijft geheel buiten de catalogus**
  ([Waarom t-strings](comparison.md)).
- **Meervouden** volgen een unie/doorsnede-regel die het meervoudssysteem
  van een doeltaal laat afwijken van dat van de bron ([spec §4](spec.md)).
- Een kapotte catalogus **valt terug in plaats van te crashen**, in lijn met
  gettexts eigen contract
  ([de handleiding](guide.md#what-happens-when-a-catalog-is-wrong)).
- En de hele conventie is een [versiebeheerde specificatie](spec.md) met een
  machineleesbare conformiteitssuite — zo geschreven dat een andere
  implementatie, inclusief een toekomstige in de standaardbibliotheek, haar
  ongewijzigd zou kunnen overnemen en interopereren.

De discussie is niet afgelopen, en dit project is er een deelnemer aan, geen
oordeel erover. Heb je productie-ervaring met gettext die deze keuzes raakt,
dan zijn [dezelfde thread][discuss-thread] en de
[Discussions][gh-discussions] van deze repository waar erover
gediscussieerd wordt.

## Tijdlijn { #timeline }

| Wanneer | Wat er gebeurde |
| --- | --- |
| midden jaren 90 | GNU gettext vestigt de PO/POT/MO-workflow die vertalers en platforms nog steeds spreken. |
| 2015 | [PEP 501] stelt interpolatiesjablonen voor, met i18n als eerste motivatie; uitgesteld. |
| 2016 | f-strings verschijnen in Python 3.6 — interpolatie krijgt haar syntaxis, en vertaling kan die niet gebruiken. |
| jul 2024 | [PEP 750] stelt t-strings voor. |
| apr 2025 | PEP 750 [geaccepteerd][sc-resolution]; PEP 501 in zijn voordeel ingetrokken. |
| aug 2025 | De thread [Support t-strings in gettext][discuss-thread] opent, met een stdlib-[pull request][cpython-pr]. |
| okt 2025 | [Python 3.14] levert t-strings; het stdlib-issue sluit als [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` verschijnt als alfa, met [spec v1](spec.md) en zijn conformiteitssuite. |

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
