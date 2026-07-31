---
description: "Co se ve skutečnosti rozbije, když se jeden malý web přeloží do pětatřiceti jazyků, které z toho za vás knihovna zachytí a které ne."
---

# Úskalí

Tento web je přeložen do pětatřiceti jazyků a každý z nich vznikl
provozováním smyčky, kterou tato dokumentace učí. Na poměry oboru je to
malý korpus a i tak stačil na to, aby narazil na většinu pastí, kvůli nimž
je i18n těžší, než vypadá.

Každá sekce níže je něco, co se tu skutečně pokazilo, jak to tehdy
vypadalo a kudy vede hranice mezi tím, co za vás knihovna kontroluje, a
tím, co zůstává na vašem úsudku.

## Přejmenování proměnné znovu odešle větu k překladu { #renaming-a-variable-retranslates-a-sentence }

Msgid je klíč katalogu a jméno interpolace je *uvnitř* něj. Přesun jedné
konstanty do modulového rozsahu a její zapsání velkými písmeny, jak žádá
pythonovský styl — `author` na `AUTHOR` — změnil
`Copyright © 2026 {author} · MIT License` ve zprávu, kterou žádný katalog
nikdy neviděl. Každý překlad toho řádku by prošel znovu fuzzy cyklem, v
každém jazyce, kvůli přejmenování, které nezměnilo nic, co by čtenář viděl.

Knihovna vás nezastaví: oba zápisy jsou platná jména zástupných symbolů.
Co ale dělá, je, že to jméno *stojí za to* chránit — interpolace musí být
[holé jméno](internals.md#from-template-to-msgid), takže tím, co je v klíči
katalogu, je slovo, které si překladatel může přečíst, ne výraz.

Zrcadlový případ je bezpečný už z podstaty. Konverze a formátovací
specifikace nejsou součástí msgid, takže zpřísnění `{amount:,.2f}` na
`{amount:,.0f}` nemění žádný klíč a nikde neznehodnotí žádný překlad.

## `nplurals=2` neznamená dva různé řetězce { #nplurals-2-does-not-mean-two-different-strings }

Turečtina, maďarština, perština i bengálština deklarují dvě formy množného
čísla a ve všech čtyřech jsou obě formy počítané zprávy zcela legitimně
*týž řetězec* — podstatné jméno zůstává po číslovce v jednotném čísle,
takže `{n} sayfa` je správně pro jednu stránku i pro deset. Recenzent,
který tu duplicitu „opraví“, překlad rozbije.

Opačná chyba je stejně snadná. Třetí forma lotyštiny existuje **jen pro
nulu**; druhá forma slovinštiny je **duál**, pro přesně dvě; poslední forma
rumunštiny vyžaduje slovo `de`, které první dvě mít nesmějí. Vyplnit tyto
pozice jednotným a množným číslem dá katalog, který je chybný jen pro
počty, jež nikdo netestuje.

Hůř, *pořadí* pozic není sémantické. Velština indexuje svých pět forem
tak, že `msgstr[0]` je obecný případ a `msgstr[1]` je jednotné číslo.
Vyplnění v pořadí, které se nabízí, umístí jednotné číslo tam, kde je najde
každá nepočítaná zpráva.

Knihovna si nic z toho nebere na sebe, a přesně o to jde: pravidlo
množného čísla cílového jazyka žije v hlavičce jeho vlastního katalogu a
[pravidlo sjednocení/průniku](spec.md) dovoluje překladu mít víc forem než
zdroj, nebo míň. Kontroluje jedinou věc, kterou zkontrolovat lze bez
znalosti jazyka — že si každá forma ponechá zástupné symboly, které
potřebuje.

## Dvě formy mohou být shodné z dobrého důvodu { #two-forms-can-be-identical-for-a-reason }

Irština má pět forem množného čísla a v hlášení o sestavení tohoto webu je
několik z nich zapsáno stejně. Není to překlep z kopírování: *leathanach*
začíná na `l` a ani jedna z počátečních mutací, které irské číslovky
spouštějí, se na `l` nepíše. Formy přesto odvádějí skutečnou práci — kmen
se střídá mezi *leathanach* a *leathanaigh* a počty nad deset se vracejí k
jednotnému číslu — ale žádné podstatné jméno s významem „stránka“ by ten
rozdíl neukázalo.

Každá kontrola, která označí duplicitní formy za podezřelé, označí
správnou irštinu. Jediným recenzentem je tu člověk, který ten jazyk zná.

## Zpráva se může shodovat jen s jedním počtem { #a-message-can-only-agree-with-one-count }

Hlášení o sestavení tohoto webu říká, kolik stránek bylo vykresleno a jak
dlouho to trvalo. Zápis „Rendered {n} pages in {seconds} seconds“ vypadá
neškodně a přeložit se nedá: gettext vybírá jednu formu podle jednoho
počtu a tím počtem je `n`. Slovo *seconds* by se muselo shodovat s číslem,
které mašinerie množného čísla nikdy nevidí.

Náprava spočívá v tom, udělat z druhé veličiny značku jednotky místo slova
— a značky jednotek se samy lokalizují: katalogy tohoto webu nesou `s`,
`с`, `ث`, `שנ׳` a `mp` a francouzská, španělská a švédská typografie chce
před značkou mezeru tam, kde ji angličtina nemá. Nic z toho není věcí
knihovny — ale všimnout si, že zpráva potřebuje *dvě* shody, věcí je, a
jediným nástrojem na to je napsat zprávu jinak.

## Úprava anglické věty upravuje cizí gramatiku { #editing-an-english-sentence-edits-foreign-grammar }

Úvodní stránka dřív říkala „all ten language editions“. Odstranění čísla —
jednoslovná úprava v angličtině, provedená proto, že to číslo pořád
zastarávalo — změnilo podmět z množného čísla na jednotné. Španělština,
italština, portugalština, ruština, ukrajinština, řečtina, nizozemština a
hebrejština musely všechny sloveso znovu shodnout; několik z nich
potřebovalo změnit i příčestí.

Úprava zdroje, která v angličtině působí triviálně, triviální dál po
proudu není. Označení jako fuzzy, což je přesně to, co `pybabel update`
dělá, je ten mechanismus, který dá každému překladateli šanci si toho
všimnout.

## Neviditelné rozdíly přežijí každé kopírování { #invisible-differences-survive-every-copy-paste }

Průvodce cituje diagnostiku obsahující `(nаme)` — záměrný escape, protože
znak, který pojmenovává, je cyrilické `а`, jež žádný čtenář od latinského
nerozezná. Překladatelé tohoto webu ten escape převedli na skutečný znak
**pětkrát nezávisle na sobě**, v pěti různých jazycích, pokaždé s
výsledkem stránky, která vypadala správně a správná nebyla.

Tohle knihovna zachytí a je to důvod, proč mají diagnostiky právě takový
tvar: zástupný symbol, jehož písmena míchají písma, je [hlášen
dvakrát](internals.md#diagnostics-are-part-of-the-design), jednou čitelně a
jednou escapovaně, protože escapovaná podoba je jediný zápis, který je od
sebe odliší. Nezlomitelná mezera uvnitř složených závorek se ze stejného
důvodu vypisuje kódovým bodem. Checker katalogů zprávu odmítne dřív, než
se stihne dostat do vydání.

## Neprázdné neznamená přeložené { #non-empty-is-not-translated }

Katalog vygenerovaný tak, že se jeho msgid zkopírují do msgstr, projde
každou naivní kontrolou: nic není prázdné, nic není fuzzy, množina zpráv
sedí přesně. Jedna edice tohoto webu takhle byla několik hodin ve vydání.
Stejně tak osm stránek jiné edice, které byly bajt po bajtu kopiemi
anglického zdroje — což projde kontrolou porovnávající mezi nimi bloky
kódu, protože jde o tentýž soubor.

Ani jedno není něco, co by překladová knihovna mohla vidět. Obojí se dá
levně otestovat, jakmile víte, že máte: porovnat se zdrojem a vyžadovat
rozdíl.

## Katalog není jediná přeložená věc { #the-catalog-is-not-the-only-translated-thing }

Dvě zdejší selhání neměla s gettextem nic společného.

Překlad nadpisu změní kotvu, která se z něj generuje, takže každý odkaz z
jiné stránky do té sekce se rozbije — potichu a jen v tom jednom jazyce.
Tento web připíná na každý nadpis anglickou kotvu a test odvozuje
očekávaný seznam z anglické stránky.

A generátor webu dodává překlady rozhraní pro šedesát osm jazyků, mezi
které svahilština ani irština nepatří. Bez nich build nespadne zpět k
angličtině; include šablony selže a edici vůbec nelze sestavit. Dva
soubory v tomto repozitáři existují právě proto, aby tuto mezeru zaplnily.

## I vaše nástroje mají chyby { #your-tools-have-bugs-too }

Krok CI, který tato dokumentace doporučuje k odhalení zastaralých
katalogů, `pybabel update --check`, tuto práci nezvládne u žádného
projektu, který používá `pgettext` nebo `npgettext` — každý katalog s
`msgctxt` hlásí jako zastaralý, při každém spuštění, kvůli chybě v tom,
jak si porovnání vyhledává zprávy. Byla nalezena tady, při pokusu ten krok
použít, nahlášena upstreamu a je [popsána v úplnosti i s náhradním
řešením](workflow.md#what-ci-gates).

Obecné poučení je to nepříjemné: brána, která je vždycky červená, je horší
než žádná brána, protože ji tým vypne. Ověřte si, že vaše kontrola v CI
vůbec může projít, dřív než jí uvěříte, že selže.

## K čemu knihovna je, v jedné větě { #what-the-library-is-for-in-one-line }

Většina této stránky je úsudek, který za vás žádný nástroj nepřevezme. Co
nástroj *umí*, je zaručit, že překlad nemůže změnit strukturu věty, kterou
překládá — nemůže hodnotu vypustit, vymyslet, přeformátovat ani sáhnout do
vašich objektů — a umí to říct větou, podle níž se ten, kdo to má opravit,
může zařídit. To je celé, co tato knihovna slibuje, a zbytek tohoto webu
je o tom, jak to dodržuje.
