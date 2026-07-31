---
description: "Kaj se v resnici pokvari, ko eno majhno spletišče prevedete v petintrideset jezikov, katere od teh težav knjižnica ujame namesto vas in katerih ne."
---

# Pasti

To spletišče je prevedeno v petintrideset jezikov in vsak od njih je nastal s
poganjanjem zanke, ki jo uči ta dokumentacija. Po merilih panoge je to majhen
korpus, pa je vseeno zadostoval, da je zadel večino pasti, zaradi katerih je
i18n težji, kot je videti.

Vsak razdelek spodaj je nekaj, kar je tu resnično šlo narobe, kakšno je bilo
tedaj videti in kje poteka meja med tem, kaj knjižnica preveri namesto vas, in
tem, kaj ostane vaša presoja.

## Preimenovanje spremenljivke pošlje poved znova v prevod { #renaming-a-variable-retranslates-a-sentence }

Msgid je katalogni ključ, ime interpolacije pa je *v njem*. Premik ene
konstante v modulski obseg in njeno zapisovanje z velikimi črkami, kakor
zahteva pythonski slog — `author` v `AUTHOR` —, je
`Copyright © 2026 {author} · MIT License` spremenil v sporočilo, ki ga ni videl
še noben katalog. Vsak prevod te vrstice bi šel znova skozi cikel oznak fuzzy,
v vsakem jeziku, in to zaradi preimenovanja, ki ni spremenilo ničesar, kar bi
bralec lahko videl.

Knjižnica vas ne bo ustavila: oba zapisa sta veljavni imeni ograd. Kar pa
naredi, je, da je ime *vredno* zaščititi — interpolacija mora biti
[preprosto ime](internals.md#from-template-to-msgid), zato je tisto, kar je v
katalognem ključu, beseda, ki jo prevajalec lahko prebere, in ne izraz.

Zrcalni primer je varen že po zgradbi. Pretvorbe in formatne specifikacije niso
del msgida, zato zaostritev `{amount:,.2f}` v `{amount:,.0f}` ne spremeni
nobenega ključa in nikjer ne razveljavi nobenega prevoda.

## `nplurals=2` ne pomeni dveh različnih nizov { #nplurals-2-does-not-mean-two-different-strings }

Turščina, madžarščina, perzijščina in bengalščina vse napovejo dve množinski
obliki in v vseh štirih sta obliki preštetega sporočila povsem upravičeno *isti
niz* — samostalnik za števnikom ostane v ednini, zato je `{n} sayfa` pravilno
za eno stran in za deset. Pregledovalec, ki to podvojitev »popravi«, prevod
pokvari.

Nasprotna napaka je prav tako lahka. Tretja oblika latvijščine obstaja **samo
za nič**; druga oblika slovenščine je **dvojina**, za natanko dve; zadnja
oblika romunščine zahteva besedico `de`, ki je prvi dve ne smeta imeti. Če ta
mesta zapolnite z ednino in množino, dobite katalog, ki je napačen le za
števila, ki jih nihče ne testira.

Še huje, *vrstni red* mest ni pomenski. Valižanščina svojih pet oblik indeksira
tako, da je `msgstr[0]` splošni primer in `msgstr[1]` ednina. Če jih izpolnite
v zaporedju, ki se ponuja, postavite ednino tja, kjer jo bo našlo vsako
neprešteto sporočilo.

Knjižnica si od tega ne vzame nič nase, in prav v tem je bistvo: množinsko
pravilo ciljnega jezika živi v glavi njegovega lastnega kataloga,
[pravilo unije/preseka](spec.md) pa prevodu dovoli imeti več oblik od izvirnika
ali manj. Preverja edino tisto, kar je brez znanja jezika sploh mogoče preveriti
— da vsaka oblika ohrani ograde, ki jih potrebuje.

## Dve obliki sta lahko enaki z razlogom { #two-forms-can-be-identical-for-a-reason }

Irščina ima pet množinskih oblik in v poročilu o gradnji tega spletišča jih je
več zapisanih enako. To ni spodrsljaj pri kopiranju: *leathanach* se začne na
`l`, nobena od začetnih premen, ki jih sprožijo irski števniki, pa se na `l` ne
zapiše. Oblike vseeno opravljajo pravo delo — koren se izmenjuje med
*leathanach* in *leathanaigh*, števila nad deset pa se vrnejo k ednini —, a
noben samostalnik s pomenom »stran« tega nasprotja ne bi pokazal.

Vsako preverjanje, ki podvojene oblike označi za sumljive, bo označilo pravilno
irščino. Edini pregledovalec za to je človek, ki ta jezik zna.

## Sporočilo se lahko ujema le z enim številom { #a-message-can-only-agree-with-one-count }

Poročilo o gradnji tega spletišča pove, koliko strani je bilo izrisanih in
koliko časa je to trajalo. Zapis »Rendered {n} pages in {seconds} seconds« je
videti neškodljiv in se ne da prevesti: gettext izbere eno obliko po enem
številu, in to število je `n`. Beseda *seconds* bi se morala ujemati s številom,
ki ga množinsko strojevje nikoli ne vidi.

Popravek je, da drugo količino zapišete kot znak enote namesto kot besedo, znaki
enot pa se sami lokalizirajo: katalogi tega spletišča nosijo `s`, `с`,
`ث`, `שנ׳` in `mp`, francoska, španska in švedska tipografija pa pred znakom
hoče presledek tam, kjer ga angleščina nima. Nič od tega ni stvar knjižnice —
opaziti, da sporočilo potrebuje *dve* ujemanji, pa je, in edino orodje za to
je, da sporočilo napišete drugače.

## Urejanje angleške povedi ureja tujo slovnico { #editing-an-english-sentence-edits-foreign-grammar }

Domača stran je nekoč govorila o »all ten language editions«. Odstranitev
števila — enobesedni poseg v angleščino, opravljen zato, ker je število ves čas
zastarevalo — je množinski osebek spremenila v ednino. Španščina,
italijanščina, portugalščina, ruščina, ukrajinščina, grščina, nizozemščina in
hebrejščina so morale vse znova uskladiti glagol; več jih je moralo spremeniti
tudi deležnik.

Poseg v izvirnik, ki se v angleščini bere kot nepomemben, nižje po toku ni
nepomemben. Označitev kot fuzzy, kar je natanko tisto, kar počne
`pybabel update`, je mehanizem, ki vsakemu prevajalcu da priložnost, da to
opazi.

## Nevidne razlike preživijo vsako kopiranje { #invisible-differences-survive-every-copy-paste }

Vodnik navaja diagnostiko, ki vsebuje `(nаme)` — namerni ubežni zapis, ker je
znak, ki ga poimenuje, cirilski `а`, ki ga noben bralec ne loči od latiničnega.
Prevajalci tega spletišča so ta ubežni zapis **petkrat, vsakič posebej**,
pretvorili v dejanski znak, v petih različnih jezikih, in vsakič je nastala
stran, ki je bila videti pravilna in je bila napačna.

To knjižnica ujame in prav to je razlog, zakaj so diagnostike takšne, kot so:
ograda, katere črke mešajo pisave, je
[javljena dvakrat](internals.md#diagnostics-are-part-of-the-design), enkrat
berljivo in enkrat ubežno zapisano, ker je ubežni zapis edina oblika, ki ju
loči. Nedeljivi presledek znotraj oklepajev se iz istega razloga izpiše po
kodni točki. Preverjevalnik katalogov sporočilo zavrne, preden lahko pride v
izdajo.

## Neprazno ni prevedeno { #non-empty-is-not-translated }

Katalog, postavljen tako, da so njegovi msgidi prepisani v msgstre, prestane
vsako naivno preverjanje: nič ni prazno, nič ni fuzzy, množica sporočil se
ujema natanko. Ena različica tega spletišča je bila v obtoku takšna več ur.
Prav tako osem strani druge različice, ki so bile bajt za bajt kopije angleškega
izvirnika — kar prestane preverjanje, ki med njima primerja bloke kode, saj gre
za isto datoteko.

Ne prvega ne drugega prevajalska knjižnica ne more videti. Oboje je poceni
preveriti, ko enkrat veste, da je treba: primerjajte z izvirnikom in zahtevajte
razliko.

## Katalog ni edina prevedena stvar { #the-catalog-is-not-the-only-translated-thing }

Dve tukajšnji odpovedi z gettextom nista imeli nič skupnega.

Prevod naslova spremeni sidro, ki se iz njega generira, zato se vsaka povezava
z druge strani v ta razdelek pokvari — tiho in samo v tem jeziku. To spletišče
na vsak naslov pripne angleško sidro, test pa pričakovani seznam izpelje iz
angleške strani.

Generator spletišča pa dobavlja prevode vmesnika za oseminšestdeset jezikov,
med katerimi ni ne svahilščine ne irščine. Brez njih se gradnja ne zateče k
angleščini; vključitev predloge odpove in različice sploh ni mogoče zgraditi.
Dve datoteki v tem repozitoriju obstajata prav zato, da to vrzel zapolnita.

## Tudi vaša orodja imajo hrošče { #your-tools-have-bugs-too }

Korak CI, ki ga ta dokumentacija priporoča za odkrivanje zastarelih katalogov,
`pybabel update --check`, tega dela ne zmore za noben projekt, ki uporablja
`pgettext` ali `npgettext`. Na Babelu 2.18.0 vsak katalog z `msgctxt` javi kot
zastarel, ob vsakem teku. Primerjava teče skozi `Catalog.is_identical`, ki
vsako sporočilo poišče po ključu, pod katerim je shranjeno — pri kontekstnem
sporočilu pa je ta ključ par `(id, context)`, ki ga `Catalog.get` ne sprejme.
Iskanje ne vrne ničesar in kataloga se nikoli ne izenačita:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Odkrit je bil tu, ob poskusu njegove uporabe, prijavljen pri viru,
nadomestno preverjanje pa je [na strani o produkciji](workflow.md#what-ci-gates).

Splošni nauk je tisti neprijetni: zaščita, ki je vedno rdeča, je slabša od
nobene zaščite, ker jo ekipa izklopi. Preverite, da vaše preverjanje v CI sploh
lahko uspe, preden mu zaupate, da bo padlo.

## Čemu je knjižnica namenjena, v eni vrstici { #what-the-library-is-for-in-one-line }

Večina te strani je presoja, ki je noben orodje ne more prevzeti. Kar orodje
*zmore*, je jamčiti, da prevod ne more spremeniti zgradbe povedi, ki jo prevaja
— ne more vrednosti izpustiti, si je izmisliti, je preoblikovati ali seči v vaše
objekte — in da to zna povedati v povedi, po kateri se tisti, ki mora to
popraviti, lahko ravna. To je vse, kar ta knjižnica obljublja, preostanek tega
spletišča pa je o tem, kako to drži.
