---
description: "Ce strică în realitate traducerea unui sit mic în treizeci și cinci de limbi, care dintre acele probleme pot fi prinse de bibliotecă în locul tău și care nu."
---

# Capcane

Situl acesta este tradus în treizeci și cinci de limbi, iar fiecare dintre ele
a fost produsă rulând bucla pe care o predă documentația de față. După
standardele industriei este un corpus mic și tot a fost de ajuns ca să
nimerească majoritatea capcanelor care fac i18n mai greu decât pare.

Fiecare secțiune de mai jos este ceva ce chiar a mers prost aici, cum arăta la
momentul respectiv și unde cade linia dintre ceea ce verifică biblioteca în
locul tău și ceea ce rămâne judecata ta.

## Redenumirea unei variabile retraduce o propoziție { #renaming-a-variable-retranslates-a-sentence }

Msgid-ul este cheia catalogului, iar un nume interpolat se află *înăuntrul*
lui. Mutarea unei singure constante la nivel de modul și scrierea ei cu
majuscule, așa cum cere stilul Python — `author` devenit `AUTHOR` —, a
transformat `Copyright © 2026 {author} · MIT License` într-un mesaj pe care
niciun catalog nu-l mai văzuse vreodată. Fiecare traducere a acelei linii ar fi
trecut din nou prin ciclul fuzzy, în fiecare limbă, pentru o redenumire care nu
schimba nimic din ce poate vedea un cititor.

Biblioteca nu te va opri: amândouă scrierile sunt nume valide de substituent.
Ce face ea totuși este să facă numele *să merite* protejat — o interpolare
trebuie să fie un [nume simplu](internals.md#from-template-to-msgid), așa că
lucrul aflat în cheia catalogului este un cuvânt pe care un traducător îl poate
citi, nu o expresie.

Cazul-oglindă este sigur prin construcție. Conversiile și specificațiile de
format nu fac parte din msgid, așa că strângerea lui `{amount:,.2f}` la
`{amount:,.0f}` nu schimbă nicio cheie și nu invalidează nicio traducere de
nicăieri.

## `nplurals=2` nu înseamnă două șiruri diferite { #nplurals-2-does-not-mean-two-different-strings }

Turca, maghiara, persana și bengaleza declară toate două forme de plural, iar
în toate patru cele două forme ale unui mesaj numărat sunt, în mod legitim,
*același șir* — substantivul rămâne la singular după un numeral, așa că
`{n} sayfa` este corect și pentru o pagină, și pentru zece. Un revizor care
„repară” duplicarea strică traducerea.

Greșeala opusă este la fel de ușor de făcut. A treia formă a letonei există
pentru **zero, singur**; a doua a slovenei este un **dual**, pentru exact doi;
ultima formă a românei cere cuvântul `de`, pe care primele două ale ei nu
trebuie să-l aibă. Umplerea acelor sloturi cu un singular și un plural produce
un catalog care este greșit numai pentru numere pe care nu le testează nimeni.

Mai rău, *ordinea* sloturilor nu este semantică. Galeza își indexează cele
cinci forme astfel încât `msgstr[0]` să fie cazul general, iar `msgstr[1]`
singularul. Completarea lor în ordinea evidentă pune singularul exact acolo
unde îl va găsi orice mesaj nenumărat.

Biblioteca nu-și asumă nimic din toate acestea, și tocmai asta e ideea: regula
de plural a limbii țintă stă în antetul propriului ei catalog, iar
[regula reuniune/intersecție](spec.md) permite ca o traducere să aibă mai multe
forme, sau mai puține, decât sursa. Ce verifică ea este singurul lucru pe care
îl poate verifica fără să cunoască limba — că fiecare formă păstrează
substituenții de care are nevoie.

## Două forme pot fi identice dintr-un motiv { #two-forms-can-be-identical-for-a-reason }

Irlandeza are cinci forme de plural, iar în raportul de build al acestui sit
mai multe dintre ele se scriu la fel. Nu este o scăpare de copy-paste:
*leathanach* începe cu `l`, iar niciuna dintre cele două mutații inițiale pe
care le declanșează numeralele irlandeze nu se scrie pe `l`. Formele fac totuși
treabă adevărată — radicalul alternează între *leathanach* și *leathanaigh*,
iar numerele peste zece revin la singular —, dar niciun substantiv care
înseamnă „pagină” nu ar arăta contrastul.

Orice verificare care semnalează formele duplicate drept suspecte va semnala
irlandeza corectă. Un om care știe limba este singurul revizor pentru asta.

## Un mesaj se poate acorda cu un singur număr { #a-message-can-only-agree-with-one-count }

Raportul de build al acestui sit spune câte pagini au fost randate și cât a
durat. Scrierea lui ca „Rendered {n} pages in {seconds} seconds” pare
inofensivă și nu este traductibilă: gettext alege o singură formă după un
singur număr, iar acel număr este `n`. Cuvântul *seconds* ar trebui să se
acorde cu un număr pe care mecanismul de plural nu-l vede niciodată.

Remediul este să faci din a doua cantitate un simbol de unitate în loc de un
cuvânt, iar simbolurile de unitate sunt ele însele localizate: cataloagele
acestui sit poartă `s`, `с`, `ث`, `שנ׳` și `mp`, iar tipografia franceză,
spaniolă și suedeză vrea un spațiu înaintea simbolului acolo unde engleza nu
vrea. Nimic din toate astea nu este treaba bibliotecii — dar observarea
faptului că un mesaj are nevoie de *două* acorduri este, iar singura unealtă
pentru asta este să scrii mesajul altfel.

## Modificarea unei propoziții englezești modifică gramatica străină { #editing-an-english-sentence-edits-foreign-grammar }

Pagina principală spunea odinioară „all ten language editions”. Eliminarea
numărului — o modificare englezească de un singur cuvânt, făcută pentru că
numărul se învechea mereu — a transformat un subiect la plural într-unul la
singular. Spaniola, italiana, portugheza, rusa, ucraineana, greaca, neerlandeza
și ebraica au trebuit toate să reacordeze verbul; câteva au avut nevoie și de
schimbarea participiului.

O modificare a sursei care se citește ca fiind banală în engleză nu este banală
mai jos pe fir. Marcarea ei ca fuzzy, adică exact ce face `pybabel update`,
este mecanismul care îi dă fiecărui traducător șansa să observe.

## Diferențele invizibile supraviețuiesc oricărui copy-paste { #invisible-differences-survive-every-copy-paste }

Ghidul citează un diagnostic care conține `(nаme)` — o escapare intenționată,
pentru că respectivul caracter este un `а` chirilic pe care niciun cititor nu-l
poate deosebi de cel latin. Traducătorii acestui sit au convertit acea escapare
în caracterul propriu-zis de **cinci ori separate**, în cinci limbi diferite,
producând de fiecare dată o pagină care arăta corect și era greșită.

Pe aceasta biblioteca chiar o prinde, și tocmai de aceea diagnosticele sunt
alcătuite așa cum sunt: un substituent ale cărui litere amestecă sisteme de
scriere este [raportat de două ori](internals.md#diagnostics-are-part-of-the-design),
o dată lizibil și o dată escapat, pentru că forma escapată este singura scriere
care le distinge. Un spațiu neîntreruptor dinăuntrul acoladelor este tipărit
prin punctul lui de cod din același motiv. Verificatorul de cataloage refuză
mesajul înainte ca acesta să poată fi livrat.

## Nevid nu înseamnă tradus { #non-empty-is-not-translated }

Un catalog schelet, cu msgid-urile copiate în msgstr-uri, trece orice
verificare naivă: nimic nu este gol, nimic nu este fuzzy, mulțimea de mesaje se
potrivește exact. O ediție a acestui sit a fost livrată așa timp de câteva ore.
La fel și opt pagini ale unei alte ediții, care erau copii identice la nivel de
octet ale sursei englezești — ceea ce trece de o verificare ce compară
blocurile de cod dintre ele, fiindcă sunt același fișier.

Niciuna dintre ele nu este ceva ce poate vedea o bibliotecă de traducere.
Amândouă sunt ieftin de testat odată ce știi că trebuie: compară cu sursa și
cere o diferență.

## Catalogul nu este singurul lucru tradus { #the-catalog-is-not-the-only-translated-thing }

Două eșecuri de aici nu au avut nimic de-a face cu gettext.

Traducerea unui titlu schimbă ancora generată din el, așa că fiecare legătură
dintr-o pagină în alta către acea secțiune se rupe — pe tăcute și numai în
limba aceea. Situl de față fixează ancora englezească pe fiecare titlu, iar un
test derivă lista așteptată din pagina englezească.

Iar generatorul de sit livrează traduceri de interfață pentru șaizeci și opt de
limbi, printre care nu se numără swahili sau irlandeza. Fără una, buildul nu
decade la engleză; includerea de șablon eșuează, iar ediția nu poate fi
construită deloc. Două dintre fișierele proprii ale acestui depozit există ca
să acopere acel gol.

## Și uneltele tale au bug-uri { #your-tools-have-bugs-too }

Pasul de CI pe care documentația de față îl recomandă pentru prinderea
cataloagelor rămase în urmă, `pybabel update --check`, nu poate face treaba
aceea pentru niciun proiect care folosește `pgettext` sau `npgettext`. Pe Babel
2.18.0 el raportă drept învechit fiecare catalog cu un `msgctxt`, la fiecare
rulare. Comparația trece prin `Catalog.is_identical`, care caută fiecare mesaj
după cheia sub care este stocat — iar pentru un mesaj cu context acea cheie este
perechea `(id, context)`, pe care `Catalog.get` nu o acceptă. Căutarea nu
întoarce nimic, iar cataloagele nu ies niciodată egale:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

A fost găsit aici încercând să fie folosit, raportat în amonte, iar verificarea
de înlocuire este [pe pagina de producție](workflow.md#what-ci-gates).

Lecția generală este cea incomodă: o poartă mereu roșie este mai rea decât
nicio poartă, pentru că o echipă o oprește. Verifică dacă verificarea ta de CI
chiar poate trece, înainte să te bizui pe ea că va pica.

## La ce servește biblioteca, într-o singură propoziție { #what-the-library-is-for-in-one-line }

Cea mai mare parte a paginii de față este judecată pe care nicio unealtă nu o
poate prelua. Ce *poate* face o unealtă este să garanteze că o traducere nu
poate schimba structura propoziției pe care o traduce — nu poate să piardă o
valoare, să inventeze una, să reformateze una sau să pătrundă în obiectele tale
— și să spună asta într-o propoziție după care poate acționa persoana care
trebuie să repare. Asta este tot ce promite biblioteca de față, iar restul
acestui sit este felul în care se ține de promisiune.
