---
description: "API czasu działania: którego punktu wejścia użyć, wiązanie katalogu, języki na żądanie, odroczone łańcuchy, wartości zależne od locale i sposób raportowania uszkodzonego tłumaczenia."
---

# Przewodnik

Ta strona to dokumentacja czasu działania: wszystko, co *kod aplikacji* robi
z tą biblioteką, gdy katalogi już istnieją. Jeśli pełna pętla — oznacz,
wyodrębnij, przetłumacz, skompiluj, uruchom — jest Ci jeszcze obca,
[samouczek](tutorial.md) przechodzi ją raz w pięć minut; tworzenie i
walidację katalogów opisuje [Ekstrakcja](extraction.md), a to, jak zespół
utrzymuje pętlę w ruchu — cykle aktualizacji, CI, platformy tłumaczeniowe —
strona [W produkcji](workflow.md).

## Którego punktu wejścia użyć? { #which-entry-point-should-i-use }

Pakiet udostępnia kilka sposobów tłumaczenia komunikatu, bo aplikacje wiążą
język na kilka różnych sposobów. Wybieraj według tego, jak Twój program
decyduje, w jakim jest języku:

| Twoja sytuacja | Użyj |
| --- | --- |
| Jeden język na cały proces — CLI, aplikacja desktopowa, skrypt | `Translator`, wywoływany jako `_` |
| Jeden język na żądanie lub na zadanie asynchroniczne — aplikacja webowa | `use_translations()` wokół pracy, a potem `tr()` |
| Komunikat zdefiniowany w czasie importu — etykieta formularza, enum, stała | `lazy_gettext()` albo `lazy_pgettext()` |
| O brzmieniu decyduje liczba | `ngettext()` / `npgettext()`, w dowolnej z powyższych form |
| Renderowanie wzorca bez udziału katalogu | `compile_template()` |

Wszystko poniżej to te pięć przypadków, w tej kolejności.

## Wiązanie katalogu { #binding-a-catalog }

Zalecany kształt odzwierciedla klasowe użycie gettext: zwiąż standardowy
obiekt tłumaczeń raz i używaj wywoływalnego procesora jako `_`.

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

Funkcje na poziomie modułu podążają za nazwami z biblioteki standardowej i
jej konwencją argumentów wyłącznie pozycyjnych:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` i `ntr` to dokładne aliasy `gettext` i `ngettext`.

## Język na żądanie { #per-request-language }

Framework webowy wybiera język per żądanie. Zwiąż tłumaczenia żądania z
bieżącym kontekstem, a każde wywołanie na poziomie modułu rozwiąże się do tego
języka, bezpiecznie przy współbieżnych żądaniach:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` wiąże bez bloku `with`, dla frameworków,
które same zarządzają cyklem życia żądania; `get_translations()` odczytuje
bieżące wiązanie. Jawny argument `translations=` zawsze wygrywa z kontekstem,
a niezwiązany kontekst wraca do globalnie zainstalowanych funkcji gettext z
biblioteki standardowej. Opracowane przykłady dla Flaska i middleware ASGI
znajdują się na stronie
[W produkcji](workflow.md#binding-a-language-at-runtime).

## Tłumaczenie odroczone { #deferred-translation }

T-string przechwytuje swoje wartości zachłannie, co jest złe dla łańcucha
zdefiniowanego w czasie importu — etykiety formularza, wartości enuma, stałej
modułu — który musi wyrenderować się w języku aktywnym w chwili jego
*użycia*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` renderuje się przez `str()`, `format()` i f-stringi oraz jest
równy swojemu wyrenderowanemu tekstowi.

!!! note "Celowo niehashowalny"

    Tekst `LazyString` zależy od aktywnego języka, więc hash zmieniałby się
    przy przełączeniu języka i po cichu psuł każdy zbiór lub słownik, który
    go przechowuje. Jeśli potrzebujesz klucza, najpierw wywołaj `str()`.

O `strict` decyduje się tam, gdzie komunikat jest zapisany, a nie tam, gdzie
się renderuje:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Łańcuch odroczony renderuje się tam, gdzie zostanie ostatecznie użyty — w
szablonie, w formularzu, w linii logu — a to miejsce rzadko wie, czy jest to
przebieg testowy, czy produkcja. Przekazanie `strict=True` przy definicji
pozwala zastosować ten sam wybór [głośno w CI, łagodnie w
produkcji](#what-happens-when-a-catalog-is-wrong) do łańcucha, który nie
renderuje się w miejscu swojego wywołania.

Formy liczby mnogiej zależą od licznika znanego w czasie działania, więc
renderuj je zachłannie przez `ngettext` tam, gdzie licznik jest znany.

## Kilka języków naraz { #several-languages-at-once }

Jedno żądanie często potrzebuje więcej niż jednego języka: strona renderowana
dla czytelnika, która przy okazji kolejkuje powiadomienie na konto ustawione
na inny, albo zestawienie cytujące każdego uczestnika w jego własnym.
Wiązania zagnieżdżają się, a wyjście z wewnętrznego bloku przywraca
zewnętrzne.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Przy liście odbiorców robotę wykonują łańcuchy odroczone: komunikat jest
zapisany raz, w czasie importu, i renderuje się raz na język.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Wiązanie jest `ContextVar`, a nie stosem trzymanym na współdzielonym
obiekcie, więc nakładające się żądania nie mogą przejąć swoich języków
nawzajem — łącznie z przypadkiem, w którym *opuszczają* swoje bloki w tej
samej kolejności, w jakiej do nich weszły, czyli tym przeplotem, który stos
rozstrzyga błędnie. Wczytywanie katalogu na każdy język jest tanie:
`gettext.translation()` parsuje każde `.mo` raz i wydaje kopie współdzielące
sparsowany katalog.

!!! warning "To, czy wątek roboczy dziedziczy wiązanie, zależy od builda"

    Goły `threading.Thread` albo `ThreadPoolExecutor.submit` startuje albo od
    kopii kontekstu wywołującego, albo od pustego, a o tym, który z nich to
    będzie, decyduje `sys.flags.thread_inherit_context` — domyślnie prawda w
    buildach free-threaded, fałsz wszędzie indziej. Ten sam kod renderuje więc
    związany język na 3.14t, a globalny dla procesu katalog na 3.14. Przekaż
    kontekst, zamiast polegać na wartości domyślnej:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` już robi to za Ciebie.

## Wartości zależne od locale { #locale-aware-values }

Ta biblioteka decyduje o tym, *gdzie* wartość pojawia się w przetłumaczonym
komunikacie. Nie lokalizuje samej wartości. `{amount:,.2f}` to pythonowa
specyfikacja formatu o ustalonym zachowaniu — przecinek co trzy cyfry i kropka
przed częścią dziesiętną — i daje te same znaki niezależnie od tego, w jakim
języku jest komunikat:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Po niemiecku ta liczba zapisuje się `1.234,50`, po francusku `1 234,50`, a
hindi grupuje `1234567` jako `12,34,567`, a nie `1,234,567`. Liczby, waluty,
daty, godziny i jednostki należą do [Babel][babel-numbers]. Najpierw sformatuj
wartość, potem wstaw gotowy łańcuch:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

W komunikacie z licznikiem liczba pełni dwie role — wybiera formę liczby
mnogiej i pojawia się w tekście — a lokalizowana jest tylko ta druga. Zachowaj
surowy licznik do wyboru formy, a do wyświetlenia przekaż sformatowany
łańcuch:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatowanie przed wywołaniem jest też tym, co trzyma specyfikację formatu
poza katalogiem: tłumacz widzi gotowy kawałek tekstu, a nie liczbę wraz z
instrukcjami jej renderowania.

## Co się dzieje, gdy katalog jest błędny { #what-happens-when-a-catalog-is-wrong }

Jeśli symbole zastępcze tłumaczenia nie pasują do źródła — brakujące,
nieznane albo przeformatowane pole, które prześlizgnęło się przez walidację,
z ręcznie edytowanego MO, katalogu od dostawcy albo potoku pomijającego
checker — domyślnym zachowaniem jest wyrenderowanie komunikatu źródłowego, a
nie zgłoszenie wyjątku. To odzwierciedla kontrakt samego gettext, że zły katalog
nigdy nie psuje aplikacji.

Przy `Hello {name}` przetłumaczonym jako `こんにちは {nombre}` renderowanie
się udaje, a do loggera `gettext_tstrings` trafia jedno ostrzeżenie:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Ostrzeżenie pojawia się raz na komunikat i wzorzec, nie raz na renderowanie,
więc uszkodzony wpis katalogu nie zalewa loga.

Do testów i CI możesz włączyć głośne niepowodzenia:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

To samo wyszukanie wtedy zgłasza wyjątek, niosący to samo zdanie bez połowy
„using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Te komunikaty są pisane dla tego, kto może na nie zareagować, a przy problemie
z katalogiem jest to częściej tłumacz niż programista — więc tam, gdzie symbol
zastępczy wygląda na obecny, a nie jest, komunikat wyjaśnia dlaczego, zamiast
powtarzać, że go brakuje. Nawiasy klamrowe pełnej szerokości, podwojone
`{{name}}`, niewidoczna twarda spacja, cyrylicka litera wśród łacińskich:
każdy z tych przypadków ma własne brzmienie, wypisane z przykładami na stronie
[Dla tłumaczy](translators.md#reading-a-failure-message). Ta strona jest
napisana tak, by przekazać ją osobie edytującej `.po`.


## Renderowanie wzorca bez katalogu { #rendering-a-pattern-without-a-catalog }

`compile_template` udostępnia tę samą maszynerię poziom niżej: zamienia
t-string na jego msgid plus związany zestaw wartości i renderuje dowolny
wzorzec, który mu podasz.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` waliduje według tych samych reguł i przy niedopasowaniu **zawsze
zgłasza wyjątek**. Nie ma tu trybu łagodnego: łagodność istnieje po to, by
wyszukanie w *katalogu* mogło zdegradować się do tekstu źródłowego, a
wzorzec, który przekazujesz samodzielnie, nie ma z czego się degradować.

## Bezpieczeństwo i zakres { #safety-and-scope }

To jest poprawne:

```python
tr(t"Hello {name}")
```

Te są odrzucane celowo:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Najpierw oblicz znaczącą wartość:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Ograniczenie daje stabilne klucze katalogu, daje tłumaczom użyteczne nazwy i
powstrzymuje przetłumaczony łańcuch przed staniem się językiem wyrażeń.

Gwarancja dotyczy *struktury i formatowania*: tłumaczenie nigdy nie jest
wykonywane i nigdy nie może dodać dostępu do atrybutów, wywołań, konwersji
ani specyfikacji formatu. Dwie rzeczy pozostają odpowiedzialnością
wywołującego, dokładnie tak jak przy stdlibowym gettext — **escapowanie**
wyrenderowanego wyniku dla jego celu (HTML, powłoka, terminal) oraz
**integralność katalogu**, bo wrogi katalog może powtarzać symbol zastępczy,
by zwielokrotnić rozmiar wyniku, co jest nieodłączne dla każdego i18n
opartego na symbolach zastępczych.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
