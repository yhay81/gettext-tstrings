---
description: "Dogovor o ogradah za tistega, ki ureja datoteke .po: kaj smete spremeniti, česa se ne smete dotakniti in kako brati napake."
---

# Za prevajalce

Ta stran je za osebo, ki ureja katalog, ne za tisto, ki piše kodo. Namenoma je
kratka in mišljena tako, da jo povežete ali prepišete v projektova lastna
navodila za prevajalce.

Nič tukaj ne zahteva, da berete Python. Vse tukaj govori o eni sami stvari: o
delih sporočila v zavitih oklepajih.

## Kaj je ograda { #what-a-placeholder-is }

Sporočilo v katalogu lahko vsebuje imena v zavitih oklepajih:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` je **ograda**. Ko program to sporočilo prikaže, `{name}` zamenja z
vrednostjo, ki jo priskrbi sam — z imenom osebe, imenom datoteke, s številom.
Ograda ni beseda za prevajanje; je reža.

Vaš prevod gre v `msgstr` in mora to režo ohraniti:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Kaj smete spremeniti in česa ne { #what-you-may-change-and-what-you-may-not }

**Smete**:

- **Ogrado premakniti** kamor koli jo hoče slovnica ciljnega jezika, tudi na
  začetek sporočila.
- **Ogrado ponoviti**, če jezik vrednost potrebuje dvakrat.
- **Prepisati vsako drugo besedo**, vključno z ločili, presledki in vrstnim
  redom povedi.

**Ne smete**:

- **Prevesti imena znotraj oklepajev.** `{name}` ostane `{name}`, tudi v
  jeziku, ki ničesar drugega ne piše z latinico.
- **Odstraniti oklepajev** ali ime zapisati brez njih.
- **Zamenjati oklepajev ASCII `{` `}` s širokima `｛` `｝`.** Mnoge vnosne
  metode proizvedejo široki obliki; videti sta skoraj enaki in ne delujeta.
- **Dodati oblikovanja**, kot je `{name!r}` ali `{amount:.2f}`. O tem, kako je
  vrednost prikazana, se odloči v programu, ne v katalogu.
- **Izmisliti si ograde**, ki je v `msgid` ni.

Če sporočilo potrebuje vrednost, ki je izvirnik ne ponuja, je to sporočilo, ki
ga mora spremeniti razvijalec. To povejte, namesto da bi si pomagali z obhodom.

## Množinske oblike { #plural-forms }

Sporočilo s številom pride z eno režo `msgstr` na množinsko obliko v vašem
jeziku, koliko jih je, pa določi vaš jezik — ena za japonščino, dve za
nemščino, tri za ruščino, šest za arabščino. Izpolnite vsako režo, ki vam jo
katalog da.

Dve pravili, ki ljudi presenetita:

- **Reže niso »ednina, množina, še bolj množina«.** Vsak indeks pomeni to, kar
  pove množinsko pravilo vašega jezika. Latvijska tretja oblika je namenjena
  samo ničli; slovenska druga je za natanko dva; valižanščina postavi splošni
  primer na indeks 0 in ednino na indeks 1.
- **Dve reži smeta upravičeno vsebovati isto besedilo.** V turščini,
  madžarščini, perzijščini in bengalščini samostalnik za števnikom ostane v
  ednini, zato sta obe obliki sporočila s številom isti niz. To je pravilno,
  ne spodrsljaj pri kopiranju.

Zgornja pravila o ogradah veljajo za vsako obliko posebej.

## Ohlapni vnosi { #fuzzy-entries }

Vnos, označen s `fuzzy`, je strojna domneva: razvijalec je spremenil izvirno
sporočilo, orodje pa je novo besedilo združilo z vašim starim prevodom, da
imate od kod začeti.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Ohlapnega vnosa **program ne uporabi** — namesto njega pokaže neprevedeni
izvirnik —, dokler nekdo besedila ne popravi in oznake `fuzzy` ne odstrani.
Večina urejevalnikov PO ima za natanko to svoj gumb.

## Kako brati sporočilo o napaki { #reading-a-failure-message }

Orodje ograde preveri ob kompilaciji kataloga, sporočilo pa je napisano za vas
in ne za programerja. Sporočiti zgolj, da `{name}` manjka, je slepa ulica,
kadar te znake vidite pred sabo, zato tam, kjer je ograda videti navzoča, pa
ni, sporočilo pove tudi zakaj. Glede na izvirnik `Hello {name}` se vsaka od
naslednjih javi pod
`translation does not match the source placeholders:`

| Vaš prevod pravi | Naveden razlog |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` manjka (oklepaja okoli njega nista znaka ASCII `{` in `}`) |
| `こんにちは {{name}}` | `{name}` manjka (zapisan je kot `{{name}}`, kar je ubežni zapis dobesednega oklepaja) |
| `こんにちは name` | `{name}` manjka (ime se pojavi, a ne znotraj oklepajev) |
| `こんにちは {名前}` | `{name}` manjka; `{名前}` ni v izvornem sporočilu |

Znaki, ki jih ni mogoče videti, so obravnavani posebej. Nedeljivi presledek
znotraj oklepajev je nekaj, kar proizvede vnosna metoda in česar noben
urejevalnik ne pokaže, zato ga sporočilo izpiše po kodni točki, namesto da bi
poimenovalo znak, ki ga nikoli ne bi mogli najti:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ime, katerega črke mešajo pisave — primer homoglifa, kjer cirilski `а` ni
razločljiv od latinskega —, je prikazano dvakrat, enkrat berljivo in enkrat
ubežno zapisano, kar je edina oblika, ki oba loči:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Isto razdvoumljanje velja, kadar grško ali cirilsko ime, zapisano povsem v eni
pisavi, trči z izvornim imenom v ASCII, vključno z enočrkovnim primerom
latinskega `a` proti cirilskemu `а`.

Če na katero od teh naletite in popravek ni očiten, je varna poteza, da ogrado,
ki ste jo vtipkali, izbrišete in prekopirate tisto iz `msgid`.

## Česa preverjanja ne zmorejo { #what-the-checks-cannot-do }

Orodje preveri, da so vaše ograde nedotaknjene. Ne more presoditi, ali je
prevod točen, naraven ali primeren za dani kontekst — to ostaja v celoti pri
vas.

Dvoje pomaga bolj kot katero koli preverjanje:

- **Preberite prevajalski komentar.** Vrstica, ki se nad sporočilom začne z
  `#.`, je razvijalčevo sporočilo, kje se pojavi in kaj pomeni.
- **Vprašajte po `msgctxt`.** Kadar se ista beseda pojavi dvakrat z različnima
  kontekstoma, je to zato, ker se morata prevesti različno — na primer »Odpri«
  kot gumb in »Odprto« kot stanje.
