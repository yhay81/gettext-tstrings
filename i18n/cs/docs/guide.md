---
description: "Běhové API: který vstupní bod použít, navázání katalogu, jazyky podle požadavku, odložené řetězce, hodnoty zohledňující locale a způsob, jakým se hlásí poškozený překlad."
---

# Průvodce

Tato stránka je referenční příručkou běhového prostředí: vše, co *kód
aplikace* dělá s touto knihovnou, jakmile katalogy existují. Pokud jste
zatím neviděli celou smyčku — označit, extrahovat, přeložit, zkompilovat,
spustit — [tutoriál](tutorial.md) ji jednou projde za pět minut; vytváření
a validaci katalogů popisuje [Extrakce](extraction.md) a to, jak tým
udržuje smyčku v chodu — aktualizační cykly, CI, překladatelské platformy —
stránka [V produkci](workflow.md).

## Který vstupní bod mám použít? { #which-entry-point-should-i-use }

Balíček exportuje několik způsobů, jak zprávu přeložit, protože aplikace
vážou jazyk několika různými způsoby. Vybírejte podle toho, jak váš program
rozhoduje, v jakém je jazyce:

| Vaše situace | Použijte |
| --- | --- |
| Jeden jazyk pro celý proces — CLI, desktopová aplikace, skript | `Translator`, volaný jako `_` |
| Jeden jazyk na požadavek nebo na asynchronní úlohu — webová aplikace | `use_translations()` kolem práce, pak `tr()` |
| Zpráva definovaná v době importu — popisek formuláře, výčet, konstanta | `lazy_gettext()` nebo `lazy_pgettext()` |
| O formulaci rozhoduje počet | `ngettext()` / `npgettext()`, v kterékoli z podob výše |
| Vykreslení vzoru bez jakéhokoli katalogu | `compile_template()` |

Všechno níže je právě těchto pět, v tomto pořadí.

## Navázání katalogu { #binding-a-catalog }

Doporučený tvar zrcadlí třídní použití gettextu: navažte standardní
překladový objekt jednou a používejte volatelný procesor jako `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Funkce na úrovni modulu se drží názvů ze standardní knihovny a její
konvence výhradně pozičních argumentů:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` a `ntr` jsou přesné aliasy `gettext` a `ngettext`.

## Jazyk podle požadavku { #per-request-language }

Webový framework volí jazyk pro každý požadavek zvlášť. Navažte překlady
požadavku na aktuální kontext a každé volání na úrovni modulu se vyhodnotí
v tomto jazyce, bezpečně i napříč souběžnými požadavky:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` navazuje bez bloku `with`, pro frameworky,
které si životní cyklus požadavku spravují samy; `get_translations()` čte
aktuální navázání. Explicitní argument `translations=` vždy vítězí nad
kontextem a nenavázaný kontext se vrací ke globálně nainstalovaným funkcím
gettext ze standardní knihovny. Propracované příklady pro Flask a ASGI
middleware najdete na stránce
[V produkci](workflow.md#binding-a-language-at-runtime).

## Odložený překlad { #deferred-translation }

T-string zachycuje své hodnoty okamžitě, což je špatně pro řetězec
definovaný v době importu — popisek formuláře, hodnotu výčtu, konstantu
modulu — který se musí vykreslit v jazyce aktivním ve chvíli, kdy je
*použit*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` se vykresluje přes `str()`, `format()` a f-stringy a rovná se
svému vykreslenému textu.

!!! note "Záměrně nehashovatelný"

    Text `LazyString` závisí na aktivním jazyce, takže hash by se při
    přepnutí jazyka změnil a potichu poškodil každou množinu nebo slovník,
    které jej drží. Potřebujete-li klíč, zavolejte nejprve `str()`.

O `strict` se rozhoduje tam, kde je zpráva napsána, ne tam, kde se
vykresluje:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Odložený řetězec se vykreslí až tam, kde je nakonec použit — v šabloně, ve
formuláři, v řádku logu — a toto místo zřídka ví, zda jde o testovací běh,
nebo o produkci. Předání `strict=True` při definici je to, co umožňuje
uplatnit tutéž volbu
[hlasitě v CI, shovívavě v produkci](#what-happens-when-a-catalog-is-wrong)
i na řetězec, který se nevykresluje v místě svého volání.

Tvary množného čísla závisejí na počtu známém až za běhu, proto je
vykreslujte okamžitě pomocí `ngettext` tam, kde je počet znám.

## Několik jazyků naráz { #several-languages-at-once }

Jediný požadavek často potřebuje více než jeden jazyk: stránku vykreslenou
pro čtenáře, která zároveň zařadí oznámení účtu nastavenému na jiný jazyk,
nebo souhrn, který každého účastníka cituje v tom jeho. Vazby se vnořují
a opuštění vnitřního bloku obnoví ten vnější.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Nad seznamem příjemců odvedou práci odložené řetězce: zpráva se napíše
jednou, při importu, a vykreslí se jednou pro každý jazyk.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Vazba je `ContextVar`, nikoli zásobník držený na sdíleném objektu, takže
překrývající se požadavky si nemohou převzít jazyk jeden druhému — včetně
případu, kdy své bloky *opouštějí* v tom pořadí, v jakém do nich vstoupily,
což je právě to prokládání, na němž zásobník selhává. Načíst katalog pro
každý jazyk je levné: `gettext.translation()` rozparsuje každé `.mo` jednou
a vydává kopie, které sdílejí rozparsovaný katalog.

!!! warning "Zda pracovní vlákno vazbu zdědí, závisí na buildu"

    Holé `threading.Thread` nebo `ThreadPoolExecutor.submit` začíná buď
    s kopií kontextu volajícího, nebo s prázdným, a které z toho, o tom
    rozhoduje `sys.flags.thread_inherit_context` — ve výchozím stavu pravdivý
    na free-threaded buildech a nepravdivý všude jinde. Tentýž kód proto
    na 3.14t vykreslí navázaný jazyk a na 3.14 procesně globální katalog.
    Předejte kontext, místo abyste spoléhali na výchozí hodnotu:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` to za vás už dělá.

## Hodnoty zohledňující locale { #locale-aware-values }

Tato knihovna rozhoduje o tom, *kde* se hodnota v přeložené zprávě objeví.
Nelokalizuje samotnou hodnotu. `{amount:,.2f}` je pythonovská formátovací
specifikace s pevným chováním — čárka po každých třech číslicích a tečka
před desetinnými místy — a produkuje tytéž znaky bez ohledu na to, v jakém
jazyce je zpráva:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Němčina totéž číslo píše `1.234,50`, francouzština `1 234,50` a hindština
seskupuje `1234567` jako `12,34,567`, nikoli `1,234,567`. Čísla, měny, data,
časy a jednotky patří [Babelu][babel-numbers]. Naformátujte hodnotu nejdřív
a teprve pak hotový řetězec vložte:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

U počítané zprávy plní číslo dvě úlohy — vybírá tvar množného čísla a
zároveň se objevuje v textu — a lokalizuje se jen ta druhá. Pro výběr si
nechte surový počet a k zobrazení předejte naformátovaný řetězec:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formátování před voláním je zároveň to, co drží formátovací specifikaci
mimo katalog: překladatel vidí hotový kus textu, ne číslo doplněné pokyny
k jeho vykreslení.

## Co se stane, když je katalog chybný { #what-happens-when-a-catalog-is-wrong }

Pokud zástupné symboly překladu neodpovídají zdroji — chybějící, neznámé
nebo přeformátované pole, které proklouzlo validací, z ručně upraveného MO,
katalogu od dodavatele nebo z pipeline, která checker přeskakuje — výchozím
chováním je vykreslit zdrojovou zprávu, nikoli vyvolat výjimku. To zrcadlí
vlastní kontrakt gettextu, podle nějž špatný katalog nikdy nerozbije
aplikaci.

S `Hello {name}` přeloženým jako `こんにちは {nombre}` vykreslení uspěje a
do loggeru `gettext_tstrings` putuje jedno varování:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Varování se objeví jednou na zprávu a vzor, nikoli jednou na vykreslení,
takže poškozený záznam katalogu nezaplaví log.

Pro testy a CI se můžete přihlásit k hlasitému selhávání:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Totéž vyhledání pak vyvolá výjimku, která nese stejnou větu bez poloviny
„using source text“:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Tyto zprávy jsou psány pro toho, kdo s nimi může něco udělat, což je u
problému s katalogem častěji překladatel než programátor — takže tam, kde
zástupný symbol vypadá jako přítomný, ale není, zpráva vysvětlí proč, místo
aby jen opakovala, že chybí. Závorky plné šířky, zdvojené `{{name}}`,
neviditelná nezlomitelná mezera, cyrilské písmeno mezi latinskými: každý
případ má vlastní formulaci a všechny jsou i s příklady vypsané na stránce
[Pro překladatele](translators.md#reading-a-failure-message). Ta stránka je
psaná tak, aby se dala předat tomu, kdo `.po` upravuje.

## Vykreslení vzoru bez katalogu { #rendering-a-pattern-without-a-catalog }

`compile_template` zpřístupňuje tutéž mašinerii o úroveň níže: promění
t-string na jeho msgid plus navázanou sadu hodnot a vykreslí libovolný
vzor, který mu předáte.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validuje podle stejných pravidel a při neshodě **vždy vyvolá
výjimku**. Žádný shovívavý režim tu není: shovívavost existuje proto, aby
se vyhledání v *katalogu* mohlo vrátit ke zdrojovému textu, a vzor, který
jste předali sami, nemá k čemu se vracet.

## Bezpečnost a rozsah { #safety-and-scope }

Toto je platné:

```python
tr(t"Hello {name}")
```

Tato volání jsou odmítnuta záměrně:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Nejprve spočítejte smysluplnou hodnotu:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Toto omezení dává stabilní klíče katalogu, dává překladatelům užitečná
jména a brání tomu, aby se přeložený řetězec stal jazykem výrazů.

Záruka je omezena na *strukturu a formátování*: překlad se nikdy
nevyhodnocuje a nikdy nemůže přidat přístup k atributům, volání, konverze
ani formátovací specifikace. Dvě věci zůstávají odpovědností volajícího,
přesně jako u gettextu ze standardní knihovny — **escapování** vykresleného
výstupu pro jeho cíl (HTML, shell, terminál) a **integrita katalogu**,
protože nepřátelský katalog může zástupný symbol opakovat, a tím znásobit
velikost výstupu, což je vlastní každé i18n založené na zástupných
symbolech.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
