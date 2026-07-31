---
description: "Dogovor med t-nizom in msgidom kot majhna verzionirana pogodba, skupaj s strojno berljivo zbirko testov skladnosti."
---

# Specifikacija

To knjižnico lahko uporabljate, ne da bi prebrali to stran — [vadnica](tutorial.md)
in [vodnik](guide.md) pokrivata vsakdanjo rabo. Ta stran je namenjena avtorjem
orodij: dogovor, ki ga knjižnica uresničuje, je zapisan kot majhna, stabilna
pogodba, da ga lahko druga izvedba — ekstraktor, IDE, preverjevalnik tipov ali
prihodnji `pygettext` — vzame za cilj in z njo sodeluje. Če želite ista pravila
razložena z razlogi in videti, kako jih izpelje referenčna izvedba, najprej
preberite [Kako deluje](internals.md).

[Preberite specifikacijo v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Pravila na enem zaslonu { #the-rules-in-one-screen }

**Msgid** je stik — v vrstnem redu iz izvorne kode — dobesednih odsekov in po
ene značke `{name}` na vsako interpolacijo. Dobesedni zaviti oklepaji so ubežno
zapisani (`{` postane `{{`). Ime mora biti preprosto ime ograde — `str.isidentifier()`
je resničen in ime ni Pythonova ključna beseda. Pretvorbe in formatne
specifikacije **niso** del msgida; ostanejo pod nadzorom aplikacije.

| t-niz | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *zavrnjeno — ni preprosto ime* |

**Prevod** je veljaven, kadar vsebuje samo gole ograde `{name}`, se vsako
zahtevano ime pojavi vsaj enkrat in se ne pojavi nobeno ime zunaj dovoljene
množice. Prerazporejanje in ponavljanje sta namenoma neomejena: oboje je lahko
v ciljnem jeziku slovnično nujno.

Pri množini je *dovoljeno* unija imen obeh vej, *zahtevano* pa njun presek —
tako `t"One file"` nasproti `t"{n} files"` pusti `n` na voljo prevajalcu
katere koli oblike, a ga ne zahteva od nobene, in množinska pravila ciljnega
jezika se smejo razlikovati od izvornih.

**Prazen msgid** se nikoli ne išče, ker ga gettext rezervira za glavo s
podatki o katalogu.

## Skladnost { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
je isti dokument v strojno berljivi obliki: primeri, ki preslikajo statično
zgradbo t-niza v msgid, ter msgid skupaj z vzorcem iz kataloga v izrisan niz
ali v zavrnitev.

Izvedba je **skladna s specifikacijo v1**, kadar ponovi vsak primer. Primeri
poimenujejo samo tisto, kar specifikacija določa — izpeljane msgide, sprejete
in zavrnjene vzorce, izrisan izhod — nikoli pa sporočila o napaki ali vrste
izjem, tako da jih izvedba v drugem jeziku lahko požene nespremenjene.

Interpolacije so opisane strukturno, nikoli kot Pythonova izvorna koda:

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

Referenčna izvedba poganja to zbirko kot del svoje testne zbirke, tako da se
besedilo in koda ne moreta tiho razhajati.

## Verzioniranje { #versioning }

To je specifikacija v1. Nazaj nezdružljiva sprememba izpeljave msgida ali
preverjanja prevodov poveča verzijo in prinese novo datoteko
`conformance/vN.json` ob obstoječi. Dodatna pojasnila, ki ne spremenijo ne
izpeljanih msgidov ne sprejetih vzorcev, tega ne storijo.
