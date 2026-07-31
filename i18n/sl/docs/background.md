---
description: "Trideset let gettexta, dva PEP-a z desetletjem vmes in razprava o standardni knjižnici, ki se je zaključila kot »not planned«: zakaj ta knjižnica obstaja, s povezavami na vire."
---

# Ozadje

Ta knjižnica stoji na stičišču dveh dolgih zgodb — ene o tem, kako se
programska oprema prevaja, in ene o tem, kako Python interpolira nize —, ki sta
se leta 2025 končno presekali in nato obtičali natanko tam, kjer bi bil potreben
majhen, premišljen dogovor. Ta stran pripoveduje obe, s povezavami na vire, ker
je zasnovne odločitve tega spletišča laže presojati, kadar vidite vprašanja, na
katera odgovarjajo.

## Ekosistem gettexta { #the-gettext-ecosystem }

[GNU gettext] je od sredine devetdesetih način, kako se prevaja prosta
programska oprema: nize v kodi označite, izvlecite jih v predlogo, prevajalcem
izročite po eno katalogno datoteko na jezik, kompilirajte, naložite med
izvajanjem. Okoli te zanke je zrasel cel ekosistem — urejevalniki PO, procesi
pregledovanja in prevajalske platforme, ki vse govorijo isti format datotek —,
Python pa v svoji standardni knjižnici že več kot dve desetletji prinaša
[modul `gettext`][stdlib-gettext]. Izvajalna polovica prevajanja nikoli ni bila
težava.

Neurejena polovica je bila zmeraj *videz niza v katalogu*. Sporočilo `%(name)s`
prevajalcem izroči sintakso printf, ki jo en sam izbrisan znak spremeni v
sesutje v produkciji; sporočilo `.format()` katalogu izroči dostop do atributov
na živih objektih. ([Zakaj t-nizi](comparison.md) prehodi oboje, z odpovedmi na
ogled.) F-nizi — sintaksa, ki jo danes največ pythonske kode postavlja na prvo
mesto — pa pri tem sploh ne morejo sodelovati: ko jih zagleda katera koli
knjižnica, so že dokončani nizi. Ljudje kljub temu poskušajo, dovolj pogosto,
da Babelov sledilnik težav te poskuse zbira ([#594][babel-594],
[#715][babel-715]); odpoved je strukturna, ne manjkajoča zmožnost.

## Dva PEP-a z desetletjem vmes { #two-peps-ten-years-apart }

Leta 2015 sta Alyssa Coghlan in Nick Humrich napisala [PEP 501] in v njem
predlagala interpolacijske predloge, katerih prvi navedeni motiv je bil i18n —
»providing a cleaner syntax for i18n translation«, kot pravi PEP sam. Predlog
je bil odložen, med drugim zato, ker je razprava pokazala, da primer i18n nosi
znatne dodatne premisleke, ki jih preprostejši primeri rabe nimajo.

Desetletje pozneje je [PEP 750] — delo Jima Bakerja, Guida van Rossuma, Paula
Everitta, Koudaija Aona, Lysandrosa Nikolaouja in Davea Pecka — zamisel oživil
kot t-nize, bil [sprejet aprila 2025][sc-resolution] in oktobra 2025 prispel v
[Python 3.14]. PEP 501 je bil zatem umaknjen njemu v prid. Ena podrobnost je za
to stran pomembna: i18n *ni* med navedenimi motivi PEP 750. PEP je mehanizem
posplošil — tip predloge, ki ga lahko uporabi katera koli knjižnica — in
vprašanje prevajanja pustil natanko tam, kjer ga je desetletje prej odložil
PEP 501: odprto.

Tako je imel jezik od Pythona 3.14 dalje natanko tisto podatkovno strukturo, ki
jo katalog sporočil potrebuje, in nobenega dogovora, kako naj se kot taka
uporablja.

## Razprava o standardni knjižnici { #the-stdlib-discussion }

Dva meseca pred izidom 3.14 je Adrian Mönnich (ThiefMaster, vzdrževalec
projekta Indico) predlagal, naj se ta vrzel zapre kar v standardni knjižnici:
nit [Support t-strings in gettext][discuss-thread] na discuss.python.org,
odprta avgusta 2025, je prišla skupaj z delujočim
[pull requestom][cpython-pr], ki je podporo t-nizom dodajal tako v `gettext`
kot v `pygettext`.

Nit je vredno prebrati v celoti, saj na dan prinese vsako težko vprašanje, na
katero je morala ta knjižnica pozneje odgovoriti:

- **Kaj sme biti interpolacija?** Samo preprosto ime ali tudi atributi in klici
  z izpeljanim imenom ograde? Vsak odgovor menja udobnost za stabilnost
  msgidov in varnost kataloga.
- **Kaj zahtevajo množinske oblike,** kadar se množinski sistem ciljnega jezika
  razlikuje od izvornega?
- **Je gettext sploh pravi cilj?** Barry Warsaw — ki je med nastajanjem
  PEP 750 zagovarjal, da t-nizi za i18n niso primerni — je kot prijaznejše
  orodje pokazal na svoj [`flufl.i18n`][flufl-i18n] in njegov slog `$`-nizov;
  drugi so zagovarjali, naj se gettext v celoti pusti za sabo v prid novejšim
  sistemom, kot je [Fluent].
- **In metavprašanje:** kar koli standardna knjižnica izda, se tako rekoč nikoli
  več ne more spremeniti. Dogovor s toliko odprtimi izbirami je tvegano
  zamrzniti že v prvem poskusu.

Soglasja ni bilo. Prijava v CPythonu je bila
[zaprta kot »not planned«][cpython-issue], pull request pa oktobra 2025, nekaj
dni po izidu 3.14, zaprt brez združitve. Zmožnost je v jeziku obstajala;
dogovor ni imel doma.

## Zakaj najprej paket { #why-a-package-first }

To je vrzel, ki jo je ta projekt sklenil zapolniti zunaj standardne knjižnice,
in sicer na premišljeno stavo: dogovor dozori hitreje tam, kjer lahko prosto
verzionira in si podporo prisluži primer za primerom, standardna knjižnica —
ki mora biti pravilna že prvič — pa je kraj, kjer naj bi se dogovor *iztekel*,
ne kjer naj bi se izdeloval.

Konkretno: vsako sporno vprašanje iz niti ima tukaj zapisan odgovor, vsakega na
svoji strani:

- Interpolacije so **samo preprosta imena**, da msgidi ostanejo stabilni in
  smiselni — [vodnik](guide.md#safety-and-scope) prikaže pravilo,
  [Kako deluje](internals.md#from-template-to-msgid) pa razloge.
- **Oblikovanje ostane povsem zunaj kataloga**
  ([Zakaj t-nizi](comparison.md)).
- **Množina** sledi pravilu unije in preseka, ki dovoli, da se množinski sistem
  ciljnega jezika razlikuje od izvornega ([specifikacija §4](spec.md)).
- Pokvarjen katalog se **vrne na izvorno besedilo, namesto da bi se sesul**, in
  s tem ohrani gettextov lastni dogovor
  ([vodnik](guide.md#what-happens-when-a-catalog-is-wrong)).
- Celoten dogovor pa je [verzionirana specifikacija](spec.md) s strojno berljivo
  zbirko testov skladnosti — napisana tako, da bi jo druga izvedba, vključno s
  prihodnjo v standardni knjižnici, lahko prevzela nespremenjeno in z njo
  sodelovala.

Razprava se ni končala in ta projekt je v njej udeleženec, ne razsodba o njej.
Če imate produkcijske izkušnje z gettextom, ki zadevajo te izbire, se o njih
prereka v [isti niti][discuss-thread] in v
[razpravah][gh-discussions] tega repozitorija.

## Časovnica { #timeline }

| Kdaj | Kaj se je zgodilo |
| --- | --- |
| sredina 1990-ih | GNU gettext vzpostavi delovni proces PO/POT/MO, ki ga prevajalci in platforme govorijo še danes. |
| 2015 | [PEP 501] predlaga interpolacijske predloge z i18n kot prvim motivom; odložen. |
| 2016 | F-nizi prispejo v Python 3.6 — interpolacija dobi svojo sintakso, prevajanje pa je ne more uporabiti. |
| jul. 2024 | [PEP 750] predlaga t-nize. |
| apr. 2025 | PEP 750 [sprejet][sc-resolution]; PEP 501 umaknjen njemu v prid. |
| avg. 2025 | Odpre se nit [Support t-strings in gettext][discuss-thread], skupaj s [pull requestom][cpython-pr] v standardni knjižnici. |
| okt. 2025 | [Python 3.14] prinese t-nize; prijava v standardni knjižnici se zapre kot [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` izide kot alfa, s [specifikacijo v1](spec.md) in njeno zbirko testov skladnosti. |

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
