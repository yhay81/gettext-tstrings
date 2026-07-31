---
description: "Treizeci de ani de gettext, două PEP-uri la zece ani distanță și discuția din biblioteca standard închisă ca neplanificată: de ce există această bibliotecă, cu legături către surse."
---

# Context

Această bibliotecă stă la punctul de întâlnire a două povești lungi — una
despre felul în care software-ul ajunge să fie tradus, alta despre felul în
care Python interpolează șiruri — care s-au intersectat în sfârșit în 2025 și
apoi s-au împotmolit exact în punctul în care era nevoie de o convenție mică și
atentă. Pagina de față spune amândouă poveștile, cu legături către surse,
pentru că deciziile de proiectare de pe acest sit sunt mai ușor de judecat
atunci când poți vedea întrebările cărora le răspund.

## Ecosistemul gettext { #the-gettext-ecosystem }

[GNU gettext] este modul în care software-ul liber ajunge să fie tradus de la
mijlocul anilor 1990: marchezi șirurile în cod, le extragi într-un șablon, dai
traducătorilor câte un fișier catalog pe limbă, compilezi, încarci la rulare.
În jurul acestei bucle a crescut un întreg ecosistem — editoare PO, fluxuri de
recenzie și platforme de traducere care vorbesc toate același format de fișier
— iar Python livrează un [modul `gettext`][stdlib-gettext] în biblioteca sa
standard de mai bine de două decenii. Jumătatea de rulare a traducerii nu a
fost niciodată problema.

Jumătatea nelămurită a fost dintotdeauna *cum arată șirul din catalog*. Un
mesaj `%(name)s` pune în mâinile traducătorilor sintaxă printf, pe care o
singură literă ștearsă o transformă într-o cădere în producție; un mesaj
`.format()` dă catalogului acces la atributele obiectelor vii.
([De ce t-stringuri](comparison.md) le parcurge pe amândouă, cu eșecurile la
vedere.) Iar f-stringurile — sintaxa pe care majoritatea codului Python o
preferă acum — nu pot participa deloc: până când vreo bibliotecă apucă să vadă
unul, el este deja un șir terminat. Lumea încearcă totuși, destul de des încât
sistemul de tichete al lui Babel să colecționeze încercările
([#594][babel-594], [#715][babel-715]); eșecul este structural, nu o
funcționalitate lipsă.

## Două PEP-uri, la zece ani distanță { #two-peps-ten-years-apart }

În 2015, Alyssa Coghlan și Nick Humrich au scris [PEP 501], propunând șabloane
de interpolare a căror primă motivație declarată era i18n — „oferirea unei
sintaxe mai curate pentru traducerea i18n”, în chiar cuvintele PEP-ului.
Propunerea a fost amânată, în parte pentru că discuția a arătat că, în cazul
i18n, intervin considerente suplimentare semnificative, pe care cazurile de
utilizare mai simple nu le aveau.

Un deceniu mai târziu, [PEP 750] — de Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou și Dave Peck — a reînviat ideea sub
formă de t-stringuri, a fost [acceptat în aprilie 2025][sc-resolution] și a
fost livrat în [Python 3.14] în octombrie 2025. PEP 501 a fost apoi retras în
favoarea lui. Un detaliu contează pentru pagina de față: i18n *nu* se numără
printre motivațiile declarate ale PEP 750. PEP-ul a generalizat mecanismul — un
tip de șablon pe care orice bibliotecă îl poate consuma — și a lăsat întrebarea
despre traducere exact acolo unde o parcase PEP 501 cu zece ani mai devreme:
deschisă.

Așadar, începând cu Python 3.14, limbajul avea exact structura de date de care
are nevoie un catalog de mesaje, și nicio convenție pentru a o folosi ca atare.

## Discuția din biblioteca standard { #the-stdlib-discussion }

Cu două luni înainte de livrarea lui 3.14, Adrian Mönnich (ThiefMaster, unul
dintre mentenanții proiectului Indico) a propus astuparea acelei lacune chiar
în biblioteca standard: firul [Support t-strings in gettext][discuss-thread] de
pe discuss.python.org, deschis în august 2025, a venit însoțit de un
[pull request][cpython-pr] funcțional care adăuga suport pentru t-stringuri
atât în `gettext`, cât și în `pygettext`.

Firul merită citit în întregime, pentru că scoate la suprafață fiecare
întrebare grea la care această bibliotecă a trebuit să răspundă mai târziu:

- **Ce poate fi o interpolare?** Doar un nume simplu, sau și atribute și
  apeluri cu un nume de substituent derivat? Fiecare răspuns face un compromis
  între comoditate, pe de o parte, și stabilitatea msgid-ului și siguranța
  catalogului, pe de alta.
- **Ce cer formele de plural,** atunci când sistemul de plural al limbii țintă
  diferă de cel al sursei?
- **Este gettext măcar ținta potrivită?** Barry Warsaw — care susținuse în
  timpul dezvoltării PEP 750 că t-stringurile nu se potrivesc bine cu i18n — a
  arătat către [`flufl.i18n`][flufl-i18n] al său și către stilul lui de
  `$`-stringuri ca fiind unealta mai prietenoasă; alții au pledat pentru a lăsa
  gettext în urmă cu totul, în favoarea unor sisteme mai noi precum [Fluent].
- **Și meta-întrebarea:** orice ar livra biblioteca standard, acel ceva nu mai
  poate practic niciodată să se schimbe. O convenție cu atâtea alegeri deschise
  este un lucru riscant de înghețat din prima încercare.

Nu s-a format niciun consens. Tichetul CPython a fost
[închis ca „not planned”][cpython-issue], iar pull requestul a fost închis
nefuzionat în octombrie 2025, la câteva zile după lansarea lui 3.14.
Capabilitatea exista în limbaj; convenția nu avea o casă.

## De ce mai întâi un pachet { #why-a-package-first }

Aceasta este lacuna pe care proiectul de față a ales să o umple din afara
bibliotecii standard, pe baza unui pariu deliberat: o convenție se maturizează
mai repede acolo unde poate schimba versiuni în voie și își poate câștiga
adoptarea caz cu caz, iar biblioteca standard — care trebuie să nimerească
lucrurile din prima — este locul în care o convenție ar trebui *să ajungă*, nu
locul în care ar trebui să fie pusă la punct.

Concret, fiecare întrebare disputată din fir are aici un răspuns consemnat în
scris, fiecare pe pagina lui:

- Interpolările sunt **doar nume simple**, așa că msgid-urile rămân stabile și
  pline de înțeles — [ghidul](guide.md#safety-and-scope) arată regula,
  [Cum funcționează](internals.md#from-template-to-msgid) motivele.
- **Formatarea rămâne complet în afara catalogului**
  ([De ce t-stringuri](comparison.md)).
- **Pluralul** urmează o regulă de reuniune/intersecție care permite ca
  sistemul de plural al unei limbi țintă să difere de cel al sursei
  ([specificația §4](spec.md)).
- Un catalog stricat **revine la sursă în loc să cadă**, păstrând contractul
  propriu al lui gettext
  ([ghidul](guide.md#what-happens-when-a-catalog-is-wrong)).
- Iar întreaga convenție este o [specificație versionată](spec.md) cu o suită
  de conformitate lizibilă de mașină — scrisă astfel încât o altă
  implementare, inclusiv una viitoare din biblioteca standard, să o poată
  adopta nemodificată și să interopereze.

Discuția nu s-a încheiat, iar acest proiect este un participant la ea, nu un
verdict asupra ei. Dacă ai experiență de producție cu gettext care are legătură
cu aceste alegeri, [același fir][discuss-thread] și
[Discuțiile][gh-discussions] acestui depozit sunt locurile unde se dezbate.

## Cronologie { #timeline }

| Când | Ce s-a întâmplat |
| --- | --- |
| mijlocul anilor 1990 | GNU gettext instituie fluxul PO/POT/MO pe care traducătorii și platformele îl vorbesc și azi. |
| 2015 | [PEP 501] propune șabloane de interpolare, cu i18n ca primă motivație; amânat. |
| 2016 | f-stringurile sunt livrate în Python 3.6 — interpolarea își capătă sintaxa, iar traducerea nu o poate folosi. |
| iul. 2024 | [PEP 750] propune t-stringurile. |
| apr. 2025 | PEP 750 [acceptat][sc-resolution]; PEP 501 retras în favoarea lui. |
| aug. 2025 | Se deschide firul [Support t-strings in gettext][discuss-thread], cu un [pull request][cpython-pr] în biblioteca standard. |
| oct. 2025 | [Python 3.14] livrează t-stringurile; tichetul din biblioteca standard se închide ca [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` este livrat ca alpha, cu [specificația v1](spec.md) și suita ei de conformitate. |

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
