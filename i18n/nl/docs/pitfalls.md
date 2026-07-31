---
description: "Wat er werkelijk stukgaat als je één kleine site in vijfendertig talen vertaalt, welke daarvan de bibliotheek voor je kan opvangen, en welke niet."
---

# Valkuilen

Deze site is vertaald in vijfendertig talen, en elk van die edities is
geproduceerd door de lus te draaien die deze documentatie leert. Dat is naar
de maatstaven van de branche een klein corpus, en het was nog steeds genoeg om
de meeste valstrikken te raken die i18n moeilijker maken dan het lijkt.

Elke sectie hieronder is iets dat hier echt is misgegaan, hoe dat er destijds
uitzag, en waar de grens ligt tussen wat de bibliotheek voor je controleert en
wat jouw oordeel blijft.

## Een variabele hernoemen hervertaalt een zin { #renaming-a-variable-retranslates-a-sentence }

De msgid is de catalogussleutel, en een geïnterpoleerde naam staat
*daarbinnen*. Eén constante naar modulescope verplaatsen en hem met
hoofdletters schrijven zoals de Python-stijl vraagt — `author` naar `AUTHOR` —
veranderde `Copyright © 2026 {author} · MIT License` in een bericht dat geen
enkele catalogus ooit had gezien. Elke vertaling van die regel zou opnieuw
door de fuzzy-cyclus zijn gegaan, in elke taal, voor een hernoeming die niets
veranderde wat een lezer kon zien.

De bibliotheek houdt je niet tegen: beide schrijfwijzen zijn geldige
placeholdernamen. Wat ze wel doet, is de naam het beschermen *waard* maken —
een interpolatie moet een [gewone naam](internals.md#from-template-to-msgid)
zijn, dus wat in de catalogussleutel staat is een woord dat een vertaler kan
lezen, geen expressie.

Het spiegelgeval is per constructie veilig. Conversies en
format-specificaties maken geen deel uit van de msgid, dus `{amount:,.2f}`
aanscherpen tot `{amount:,.0f}` verandert geen sleutel en maakt nergens een
vertaling ongeldig.

## `nplurals=2` betekent niet twee verschillende strings { #nplurals-2-does-not-mean-two-different-strings }

Turks, Hongaars, Perzisch en Bengaals verklaren alle vier twee
meervoudsvormen, en in alle vier zijn de twee vormen van een geteld bericht
legitiem *dezelfde string* — het zelfstandig naamwoord blijft enkelvoud na een
telwoord, dus `{n} sayfa` klopt voor één pagina en voor tien. Een reviewer die
de duplicatie "repareert", breekt de vertaling.

De omgekeerde fout is net zo makkelijk. De derde vorm van het Lets bestaat
**alleen voor nul**; de tweede van het Sloveens is een **dualis**, voor precies
twee; de laatste vorm van het Roemeens vereist het woord `de` dat de eerste
twee juist niet mogen hebben. Die plekken vullen met een enkelvoud en een
meervoud levert een catalogus op die alleen fout is voor tellingen die niemand
test.

Erger nog: de *volgorde* van de plekken is niet semantisch. Het Wels indexeert
zijn vijf vormen zo dat `msgstr[0]` het algemene geval is en `msgstr[1]` het
enkelvoud. Ze in de voor de hand liggende volgorde invullen zet het enkelvoud
precies daar waar elk ongeteld bericht het zal vinden.

De bibliotheek neemt hier niets van op zich, en dat is het punt: de
meervoudsregel van de doeltaal staat in haar eigen catalogusheader, en de
[unie/doorsnede-regel](spec.md) laat een vertaling meer of minder vormen
hebben dan de bron. Wat ze wel controleert is het enige dat ze kan
controleren zonder de taal te kennen — dat elke vorm de placeholders behoudt
die hij nodig heeft.

## Twee vormen kunnen met reden identiek zijn { #two-forms-can-be-identical-for-a-reason }

Het Iers heeft vijf meervoudsvormen, en in het buildrapport van deze site zijn
er verschillende hetzelfde gespeld. Dat is geen kopieerfout: *leathanach*
begint met een `l`, en geen van beide beginmutaties die Ierse telwoorden
oproepen wordt op een `l` geschreven. De vormen doen nog steeds echt werk — de
stam wisselt tussen *leathanach* en *leathanaigh*, en tellingen boven de tien
keren terug naar het enkelvoud — maar geen zelfstandig naamwoord dat "pagina"
betekent zou het contrast laten zien.

Elke controle die dubbele vormen als verdacht markeert, markeert correct Iers.
Een mens die de taal kent is hiervoor de enige reviewer.

## Een bericht kan maar met één telling congrueren { #a-message-can-only-agree-with-one-count }

Het buildrapport van deze site vertelt hoeveel pagina's er gerenderd zijn en
hoe lang dat duurde. Dat schrijven als "Rendered {n} pages in {seconds}
seconds" ziet er onschuldig uit en is niet vertaalbaar: gettext kiest één vorm
op grond van één telling, en die telling is `n`. Het woord *seconds* zou
moeten congrueren met een getal dat het meervoudsmechanisme nooit te zien
krijgt.

De oplossing is om van de tweede hoeveelheid een eenheidssymbool te maken in
plaats van een woord, en eenheidssymbolen zijn zelf ook gelokaliseerd: de
catalogi van deze site dragen `s`, `с`, `ث`, `שנ׳` en `mp`, en de Franse,
Spaanse en Zweedse typografie wil een spatie vóór het symbool waar het Engels
dat niet doet. Niets daarvan is de zaak van de bibliotheek — maar opmerken dat
een bericht *twee* congruenties nodig heeft wel, en het enige gereedschap
daarvoor is het bericht anders schrijven.

## Een Engelse zin bewerken bewerkt vreemde grammatica { #editing-an-english-sentence-edits-foreign-grammar }

Op de startpagina stond ooit "all ten language editions". Het getal
verwijderen — een Engelse bewerking van één woord, gedaan omdat het getal
steeds verouderde — maakte een meervoudig onderwerp enkelvoudig. Spaans,
Italiaans, Portugees, Russisch, Oekraïens, Grieks, Nederlands en Hebreeuws
moesten allemaal het werkwoord opnieuw laten congrueren; bij verschillende
moest ook het deelwoord veranderen.

Een bronbewerking die in het Engels triviaal leest, is dat stroomafwaarts
niet. Ze fuzzy markeren, wat `pybabel update` doet, is het mechanisme dat elke
vertaler de kans geeft het op te merken.

## Onzichtbare verschillen overleven elke copy-paste { #invisible-differences-survive-every-copy-paste }

De handleiding citeert een diagnostiek die `(nаme)` bevat — een bewuste
escape, want het teken dat ze noemt is een Cyrillische `а` die geen lezer van
de Latijnse kan onderscheiden. Vertalers van deze site hebben die escape **vijf
afzonderlijke keren** in het echte teken veranderd, in vijf verschillende
talen, en produceerden elke keer een pagina die er correct uitzag en fout was.

Deze vangt de bibliotheek wél, en het is de reden dat de diagnostiek gevormd
is zoals ze is: een placeholder waarvan de letters schriftsystemen mengen
wordt [twee keer gemeld](internals.md#diagnostics-are-part-of-the-design), één
keer leesbaar en één keer geëscaped, omdat de geëscapete vorm de enige
schrijfwijze is die ze onderscheidt. Een no-break space binnen accolades wordt
om dezelfde reden per codepunt afgedrukt. De cataloguschecker weigert het
bericht voordat het kan uitgaan.

## Niet-leeg is niet vertaald { #non-empty-is-not-translated }

Een catalogus die is opgezet met zijn msgids gekopieerd naar de msgstrs
doorstaat elke naïeve controle: niets is leeg, niets is fuzzy, de
berichtenverzameling komt exact overeen. Eén editie van deze site heeft
enkele uren zo live gestaan. Dat gold ook voor acht pagina's van een andere
editie die byte-identieke kopieën van de Engelse bron waren — wat een controle
die codeblokken tussen beide vergelijkt doorstaat, omdat het hetzelfde bestand
is.

Geen van beide is iets dat een vertaalbibliotheek kan zien. Beide zijn goedkoop
te testen zodra je weet dat het moet: vergelijk met de bron en eis een
verschil.

## De catalogus is niet het enige vertaalde ding { #the-catalog-is-not-the-only-translated-thing }

Twee storingen hier hadden niets met gettext te maken.

Een kop vertalen verandert het anker dat eruit gegenereerd wordt, dus elke
kruisverwijzing naar die sectie breekt — stilletjes, en alleen in die taal.
Deze site pint op elke kop het Engelse anker vast, en een test leidt de
verwachte lijst af uit de Engelse pagina.

En de sitegenerator levert interfacevertalingen voor achtenzestig talen, en
daar zitten Swahili en Iers niet bij. Zonder zo'n vertaling valt de build niet
terug op het Engels; de template-include mislukt en de editie kan helemaal
niet gebouwd worden. Twee bestanden in deze repository bestaan om dat gat te
vullen.

## Je gereedschap heeft ook bugs { #your-tools-have-bugs-too }

De CI-stap die deze documentatie aanbeveelt om verouderde catalogi op te
sporen, `pybabel update --check`, kan dat werk niet doen voor een project dat
`pgettext` of `npgettext` gebruikt. Op Babel 2.18.0 meldt hij elke catalogus
met een `msgctxt` als verouderd, bij elke run. De vergelijking loopt via
`Catalog.is_identical`, dat elk bericht opzoekt onder de sleutel waaronder
het is opgeslagen — en voor een contextueel bericht is die sleutel het paar
`(id, context)`, dat `Catalog.get` niet accepteert. De opzoeking levert
niets op, en de catalogi zijn dus nooit gelijk:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Hij is hier gevonden door hem te willen gebruiken, upstream gemeld, en de
vervangende controle staat [op de productiepagina](workflow.md#what-ci-gates).

De algemene les is de ongemakkelijke: een poort die altijd rood staat is erger
dan geen poort, want een team zet hem uit. Controleer of je CI-check echt kan
slagen voordat je erop vertrouwt dat hij faalt.

## Waar de bibliotheek voor is, in één regel { #what-the-library-is-for-in-one-line }

Het meeste op deze pagina is oordeelsvermogen dat geen enkel gereedschap kan
overnemen. Wat een gereedschap *wel* kan, is garanderen dat een vertaling de
structuur van de zin die ze vertaalt niet kan veranderen — geen waarde kan
weglaten, er een verzinnen, er een anders opmaken, of in je objecten grijpen —
en dat kan zeggen in een zin waarmee degene die het moet repareren iets kan.
Dat is alles wat deze bibliotheek belooft, en de rest van deze site is hoe ze
die belofte nakomt.
