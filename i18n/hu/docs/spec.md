---
description: "A t-string → msgid konvenció mint kicsi, verziózott szerződés, géppel olvasható konformitási készlettel."
---

# Specifikáció

Ezt a könyvtárat úgy is használhatod, hogy ezt az oldalt el sem olvasod — a
mindennapi használatot az [oktatóanyag](tutorial.md) és a
[kézikönyv](guide.md) fedi le. Ez az oldal eszközkészítőknek szól: a
könyvtár által megvalósított konvenciót kicsi, stabil szerződésként írtuk le,
hogy egy másik megvalósítás — egy kinyerő, egy IDE, egy típusellenőrző vagy
egy jövőbeli `pygettext` — megcélozhassa, és együttműködhessen vele. Ha
ugyanezeket a szabályokat az okaikkal együtt szeretnéd látni, és azt, hogyan
hajtja végre őket a referencia-megvalósítás, előbb a
[Hogyan működik](internals.md) oldalt olvasd el.

[Olvasd el a v1-es specifikációt :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## A szabályok egy képernyőn { #the-rules-in-one-screen }

**A msgid** a literális szakaszok és interpolációnként egy `{name}` token
összefűzése forrásbeli sorrendben. A literális kapcsos zárójeleket
escape-eljük (a `{` `{{` lesz). A névnek egyszerű helyőrzőnévnek kell lennie —
a `str.isidentifier()` igaz rá, és nem Python-kulcsszó. A konverziók és a
formátumleírók **nem** részei a msgidnek; az alkalmazás felügyelete alatt
maradnak.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *elutasítva — nem egyszerű név* |

**Egy fordítás** akkor érvényes, ha csak puszta `{name}` helyőrzőket
tartalmaz, minden kötelező név legalább egyszer megjelenik benne, és nem
jelenik meg a megengedett halmazon kívüli név. Az átrendezés és az ismétlés
szándékosan korlátozatlan: mindkettő lehet nyelvtanilag szükséges a
célnyelvben.

Többes számoknál a *megengedett* az ágak neveinek uniója, a *kötelező* pedig a
metszetük — így a `t"One file"` a `t"{n} files"` ellenében az `n` nevet
elérhetővé teszi bármelyik alak fordítója számára, de egyikben sem teszi
kötelezővé, a célnyelv többesszám-szabályai pedig eltérhetnek a
forrásnyelvéitől.

**Az üres msgidet** soha nem keressük ki, mert a gettext a katalógus
metaadat-fejlécének tartja fenn.

## Konformitás { #conformance }

A
[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
ugyanez a dokumentum géppel olvasható formában: esetek, amelyek egy t-string
statikus szerkezetét msgidre, illetve egy msgidet plusz egy katalógusbeli
mintát renderelt szövegre vagy elutasításra képeznek le.

Egy megvalósítás akkor **felel meg a v1-es specifikációnak**, ha minden esetet
reprodukál. Az esetek csak azt nevezik meg, amit a specifikáció meghatároz —
levezetett msgideket, elfogadott és elutasított mintákat, renderelt kimenetet
—, hibaüzenetet vagy kivételtípust soha, így egy másik nyelvű megvalósítás is
változtatás nélkül futtathatja őket.

Az interpolációkat szerkezetileg írjuk le, soha nem Python-forrásként:

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

A `"spec"` mező **nem** specifikációverzió — a `v1.json` minden esete a v1-es
specifikációhoz tartozik. Azt nevezi meg, hogy a `SPEC.md` melyik szakaszát
gyakorolja az eset, tehát a `"2.2"` §2.2-ként olvasandó: ez a helyőrzőtoken
levezetésének szabálya.

A referencia-megvalósítás a saját tesztkészlete részeként futtatja a
készletet, így a szöveg és a kód nem sodródhat szét csendben.

## Verziózás { #versioning }

Ez a v1-es specifikáció. A msgid-levezetés vagy a fordításellenőrzés
visszafelé nem kompatibilis változása növeli a verziószámot, és a meglévő
mellé új `conformance/vN.json` fájlt szállít. Azok a kiegészítő pontosítások,
amelyek sem a levezetett msgideket, sem az elfogadott mintákat nem
változtatják meg, nem.