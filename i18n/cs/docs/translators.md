---
description: "Kontrakt o zástupných symbolech pro toho, kdo upravuje soubory .po: co měnit smíte, co musíte nechat být a jak číst chybová hlášení."
---

# Pro překladatele

Tato stránka je pro toho, kdo upravuje katalog, ne pro toho, kdo píše kód.
Je záměrně krátká a je určená k tomu, aby se dala odkázat nebo zkopírovat
do vlastních pokynů pro překladatele daného projektu.

Nic z toho, co je tady, po vás nechce, abyste uměli číst Python. Všechno tady
je o jediné věci: o kouscích zprávy ve složených závorkách.

## Co je zástupný symbol { #what-a-placeholder-is }

Zpráva v katalogu může obsahovat jména ve složených závorkách:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` je **zástupný symbol**. Když program tuto zprávu zobrazí, nahradí
`{name}` hodnotou, kterou sám dodá — jménem osoby, názvem souboru, číslem.
Zástupný symbol není slovo k překladu; je to prázdné místo.

Váš překlad patří do `msgstr` a musí toto místo zachovat:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Co měnit smíte a co ne { #what-you-may-change-and-what-you-may-not }

**Smíte**:

- **Přesunout zástupný symbol** kamkoli, kam ho gramatika cílového jazyka
  chce, včetně úplného začátku zprávy.
- **Zopakovat zástupný symbol**, potřebuje-li jazyk tutéž hodnotu dvakrát.
- **Přepsat každé ostatní slovo**, včetně interpunkce, mezer a pořadí vět.

**Nesmíte**:

- **Překládat jméno uvnitř závorek.** `{name}` zůstává `{name}` i v jazyce,
  který jinak nepíše latinkou vůbec nic.
- **Odstranit závorky** ani napsat jméno bez nich.
- **Nahradit ASCII závorky `{` `}` závorkami plné šířky `｛` `｝`.** Mnohé
  vstupní metody produkují podoby plné šířky; vypadají skoro stejně a
  nefungují.
- **Přidat formátování**, například `{name!r}` nebo `{amount:.2f}`. O tom,
  jak se hodnota zobrazí, se rozhoduje v programu, ne v katalogu.
- **Vymyslet si zástupný symbol**, který v `msgid` není.

Pokud zpráva potřebuje hodnotu, kterou originál nenabízí, je to zpráva, již
musí změnit vývojář. Řekněte to, místo abyste to obcházeli.

## Tvary množného čísla { #plural-forms }

Počítaná zpráva přichází s jedním políčkem `msgstr` na každý tvar množného
čísla vašeho jazyka a kolik jich je, o tom rozhoduje váš jazyk — jeden pro
japonštinu, dva pro němčinu, tři pro ruštinu, šest pro arabštinu. Vyplňte
každé políčko, které vám katalog dá.

Dvě pravidla, na kterých lidé chybují:

- **Ta políčka nejsou „jednotné číslo, množné číslo, ještě množnější“.**
  Každý index znamená to, co říká pravidlo množného čísla vašeho jazyka.
  Třetí tvar lotyštiny je jen pro nulu; druhý tvar slovinštiny je přesně pro
  dva; velština dává obecný případ na index 0 a jednotné číslo na index 1.
- **Dvě políčka mohou právem obsahovat tentýž text.** V turečtině,
  maďarštině, perštině a bengálštině zůstává podstatné jméno po číslovce
  v jednotném čísle, takže oba tvary počítané zprávy jsou tentýž řetězec.
  To je správně, ne přehmat při kopírování.

Pravidla o zástupných symbolech výše platí pro každý tvar zvlášť.

## Záznamy fuzzy { #fuzzy-entries }

Záznam označený jako `fuzzy` je strojový odhad: vývojář změnil původní
zprávu a nástroje spárovaly nový text s vaším starým překladem, abyste měli
od čeho začít.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Fuzzy záznam program **nepoužívá** — místo něj zobrazí nepřeložený originál
— dokud text někdo nezreviduje a značku `fuzzy` neodstraní. Většina PO
editorů na to má tlačítko.

## Čtení zprávy o selhání { #reading-a-failure-message }

Nástroje kontrolují zástupné symboly při kompilaci katalogu a hlášení je
psané pro vás, ne pro programátora. Hlásit jen to, že `{name}` chybí, je
slepá ulička, když ty znaky vidíte před sebou — takže tam, kde zástupný
symbol vypadá jako přítomný, ale není, zpráva říká proč. Vůči originálu
`Hello {name}` je každý z následujících případů hlášen pod
`translation does not match the source placeholders:`

| Váš překlad říká | Uvedený důvod |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Znaky, které nelze vidět, dostávají vlastní zacházení. Nezlomitelná mezera
uvnitř složených závorek je něco, co vyprodukuje vstupní metoda a co žádný
editor nezobrazí, takže zpráva ji vypíše jako kódový bod, místo aby
jmenovala znak, který byste nikdy nenašli:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Jméno, jehož písmena míchají písemné soustavy — případ homoglyfů, kdy je
cyrilské `а` k nerozeznání od latinského — se zobrazí dvakrát, jednou
čitelně a jednou v escapované podobě, jediné, která je od sebe odliší:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Stejné rozlišení se uplatní, když řecké nebo cyrilské jméno zapsané celé
jedním písmem koliduje s ASCII jménem ve zdroji, včetně jednopísmenného
případu latinského `a` a cyrilského `а`.

Narazíte-li na některý z těchto případů a oprava není zřejmá, bezpečným
krokem je smazat zástupný symbol, který jste napsali, a zkopírovat ten
z `msgid`.

## Co kontroly nedokážou { #what-the-checks-cannot-do }

Nástroje ověřují, že vaše zástupné symboly jsou nedotčené. Nedokážou
posoudit, zda je překlad přesný, přirozený nebo správný pro daný kontext —
to zůstává výhradně na vás.

Dvě věci pomohou víc než jakákoli kontrola:

- **Čtěte komentář pro překladatele.** Řádek začínající `#.` nad zprávou je
  vývojář, který vám říká, kde se zpráva objevuje a co znamená.
- **Ptejte se na `msgctxt`.** Objeví-li se totéž slovo dvakrát s různými
  kontexty, je to proto, že se ty dva výskyty mají přeložit odlišně —
  například „Open“ jako tlačítko a „Open“ jako stav.
