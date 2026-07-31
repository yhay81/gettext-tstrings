---
description: "Konvence t-string na msgid jako malý verzovaný kontrakt, s strojově čitelnou sadou testů konformity."
---

# Specifikace

Tuto knihovnu můžete používat, aniž byste tuto stránku četli —
[tutoriál](tutorial.md) a [průvodce](guide.md) pokrývají každodenní
použití. Tato stránka je pro autory nástrojů: konvence, kterou knihovna
implementuje, je sepsána jako malý, stabilní kontrakt, aby na něj mohla
mířit jiná implementace — extraktor, IDE, typový kontrolor nebo budoucí
`pygettext` — a spolupracovat s ním. Tatáž pravidla vysvětlená i s důvody —
a to, jak je provádí referenční implementace — najdete nejprve na stránce
[Jak to funguje](internals.md).

[Přečíst spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Pravidla na jedné obrazovce { #the-rules-in-one-screen }

**Msgid** je zřetězení, ve zdrojovém pořadí, literálních segmentů a
jednoho tokenu `{name}` na každou interpolaci. Literální složené závorky
se escapují (`{` se stane `{{`). Jméno musí být prosté jméno zástupného
symbolu — `str.isidentifier()` vrací pravdu a nejde o klíčové slovo
Pythonu. Konverze a formátovací specifikace **nejsou** součástí msgid;
zůstávají pod kontrolou aplikace.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *odmítnuto — není prosté jméno* |

**Překlad** je platný, když obsahuje výhradně holé zástupné symboly
`{name}`, každé vyžadované jméno se vyskytuje alespoň jednou a nevyskytuje
se žádné jméno mimo množinu povolených. Přeuspořádání a opakování jsou
záměrně neomezené: obojí může být v cílovém jazyce gramaticky nutné.

Pro množné číslo je *povolené* sjednocením jmen obou větví a *vyžadované*
jejich průnikem — takže `t"One file"` vůči `t"{n} files"` nechává `n`
dostupné překladateli obou tvarů, avšak vyžadované v žádném z nich, a
pravidla množného čísla cílového jazyka se mohou lišit od zdrojových.

**Prázdný msgid** se nikdy nevyhledává, protože gettext jej vyhrazuje pro
hlavičku metadat katalogu.

## Konformita { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
je tentýž dokument ve strojově čitelné podobě: případy mapující statickou
strukturu t-stringu na msgid a msgid plus katalogový vzor na vykreslený
řetězec nebo odmítnutí.

Implementace **je konformní se spec v1**, když reprodukuje každý případ.
Případy pojmenovávají pouze to, co specifikace definuje — odvozené msgid,
přijímané a odmítané vzory, vykreslený výstup — a nikdy chybovou zprávu
ani typ výjimky, takže implementace v jiném jazyce je může spustit beze
změn.

Interpolace se popisují strukturálně, nikdy jako pythonovský zdrojový kód:

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

Referenční implementace spouští tuto sadu jako součást vlastních testů,
takže se próza a kód nemohou potichu rozejít.

## Verzování { #versioning }

Toto je spec v1. Zpětně nekompatibilní změna v odvozování msgid nebo ve
validaci překladů zvyšuje verzi a dodává nový `conformance/vN.json` vedle
stávajícího. Aditivní upřesnění, která nemění ani odvozené msgid, ani
přijímané vzory, verzi nezvyšují.
