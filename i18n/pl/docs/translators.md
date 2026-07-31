---
description: "Kontrakt symboli zastępczych dla osoby edytującej pliki .po: co możesz zmieniać, czego musisz nie ruszać i jak czytać komunikaty o błędach."
---

# Dla tłumaczy

Ta strona jest dla osoby edytującej katalog, nie dla osoby piszącej kod. Jest
krótka celowo i ma służyć do podlinkowania albo skopiowania do własnych
instrukcji projektu dla tłumaczy.

Nic tutaj nie wymaga umiejętności czytania Pythona. Wszystko dotyczy jednej
rzeczy: fragmentów komunikatu w nawiasach klamrowych.

## Czym jest symbol zastępczy { #what-a-placeholder-is }

Komunikat w katalogu może zawierać nazwy w nawiasach klamrowych:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` to **symbol zastępczy**. Gdy program pokazuje ten komunikat, zastępuje
`{name}` wartością, którą sam dostarcza — imieniem osoby, nazwą pliku, liczbą.
Symbol zastępczy nie jest słowem do przetłumaczenia; to miejsce na wartość.

Twoje tłumaczenie trafia do `msgstr` i musi zachować to miejsce:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Co możesz zmieniać, a czego nie { #what-you-may-change-and-what-you-may-not }

**Możesz**:

- **Przenieść symbol zastępczy** wszędzie tam, gdzie chce go gramatyka języka
  docelowego, także na początek komunikatu.
- **Powtórzyć symbol zastępczy**, jeśli język potrzebuje wartości dwa razy.
- **Przepisać każde inne słowo**, łącznie z interpunkcją, odstępami i
  szykiem zdania.

**Nie wolno Ci**:

- **Tłumaczyć nazwy wewnątrz klamer.** `{name}` pozostaje `{name}`, nawet w
  języku, który poza tym nie pisze niczego alfabetem łacińskim.
- **Usuwać klamer** ani pisać nazwy bez nich.
- **Zastępować klamer ASCII `{` `}` pełnoszerokościowymi `｛` `｝`.** Wiele
  metod wprowadzania produkuje formy pełnoszerokościowe; wyglądają niemal
  identycznie i nie działają.
- **Dodawać formatowania**, takiego jak `{name!r}` czy `{amount:.2f}`. O tym,
  jak wartość jest wyświetlana, decyduje program, nie katalog.
- **Wymyślać symbolu zastępczego**, którego nie ma w `msgid`.

Jeśli komunikat potrzebuje wartości, której oryginał nie oferuje, to komunikat,
który musi zmienić deweloper. Powiedz o tym, zamiast to obchodzić.

## Formy liczby mnogiej { #plural-forms }

Komunikat z licznikiem przychodzi z jednym slotem `msgstr` na każdą formę
liczby mnogiej w Twoim języku, a to Twój język decyduje, ile ich jest — jedna
dla japońskiego, dwie dla niemieckiego, trzy dla rosyjskiego, sześć dla
arabskiego. Wypełnij każdy slot, który daje Ci katalog.

Dwie reguły, na których ludzie się potykają:

- **Sloty to nie „pojedyncza, mnoga, bardziej mnoga".** Każdy indeks znaczy to,
  co mówi reguła liczby mnogiej Twojego języka. Trzecia forma łotewskiego jest
  wyłącznie dla zera; druga słoweńskiego dla dokładnie dwóch; walijski umieszcza
  przypadek ogólny pod indeksem 0, a pojedynczą pod indeksem 1.
- **Dwa sloty mogą zasadnie zawierać ten sam tekst.** W tureckim, węgierskim,
  perskim i bengalskim rzeczownik po liczebniku pozostaje w liczbie
  pojedynczej, więc obie formy komunikatu z licznikiem to ten sam łańcuch. To
  poprawne, a nie pomyłka przy kopiowaniu.

Powyższe reguły symboli zastępczych stosują się do każdej formy osobno.

## Wpisy fuzzy { #fuzzy-entries }

Wpis oznaczony jako `fuzzy` to zgadywanie maszyny: deweloper zmienił oryginalny
komunikat, a narzędzia sparowały nowy tekst z Twoim starym tłumaczeniem, żebyś
miał od czego zacząć.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Wpis fuzzy **nie jest używany przez program** — zamiast niego pokazuje się
nieprzetłumaczony oryginał — dopóki ktoś nie poprawi tekstu i nie usunie
znacznika `fuzzy`. Większość edytorów PO ma na to osobny przycisk.

## Czytanie komunikatu o błędzie { #reading-a-failure-message }

Narzędzia sprawdzają symbole zastępcze przy kompilacji katalogu, a komunikat
jest napisany dla Ciebie, a nie dla programisty. Zgłoszenie samego tego, że
brakuje `{name}`, jest ślepą uliczką, gdy widzisz te znaki przed sobą, więc tam,
gdzie symbol zastępczy wygląda na obecny, choć nie jest, komunikat mówi
dlaczego. Względem oryginału `Hello {name}` każdy z poniższych jest zgłaszany
pod nagłówkiem `translation does not match the source placeholders:`

| Twoje tłumaczenie mówi | Podany powód |
| --- | --- |
| `こんにちは ｛name｝` | brakuje `{name}` (klamry wokół niego to nie ASCII `{` i `}`) |
| `こんにちは {{name}}` | brakuje `{name}` (zapisano `{{name}}`, czyli tak, jak escape'uje się dosłowną klamrę) |
| `こんにちは name` | brakuje `{name}` (nazwa się pojawia, ale nie w klamrach) |
| `こんにちは {名前}` | brakuje `{name}`; `{名前}` nie występuje w komunikacie źródłowym |

Znaki, których nie da się zobaczyć, dostają własne traktowanie. Spacja
niełamiąca wewnątrz klamer to coś, co produkuje metoda wprowadzania i czego nie
pokazuje żaden edytor, więc komunikat wypisuje ją po punkcie kodowym, zamiast
nazywać znak, którego nigdy byś nie znalazł:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nazwa, której litery mieszają systemy pisma — przypadek homoglifu, gdzie
cyrylickie `а` jest nieodróżnialne od łacińskiego — jest pokazana dwa razy: raz
czytelnie i raz z escape'ami, co jest jedyną formą pozwalającą odróżnić jedno od
drugiego:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

To samo ujednoznacznienie stosuje się, gdy grecka lub cyrylicka nazwa zapisana w
całości jednym pismem koliduje z nazwą źródłową w ASCII, łącznie z
jednoliterowym przypadkiem łacińskiego `a` / cyrylickiego `а`.

Jeśli natkniesz się na jeden z tych przypadków, a poprawka nie jest oczywista,
bezpiecznym ruchem jest usunięcie wpisanego przez siebie symbolu zastępczego i
skopiowanie tego z `msgid`.

## Czego kontrole nie potrafią { #what-the-checks-cannot-do }

Narzędzia weryfikują, że Twoje symbole zastępcze są nienaruszone. Nie potrafią
stwierdzić, czy tłumaczenie jest wierne, naturalne albo właściwe dla kontekstu —
to zostaje w całości po Twojej stronie.

Dwie rzeczy pomagają bardziej niż jakakolwiek kontrola:

- **Przeczytaj komentarz dla tłumacza.** Linia zaczynająca się od `#.` nad
  komunikatem to deweloper mówiący Ci, gdzie ten komunikat się pojawia i co
  znaczy.
- **Pytaj o `msgctxt`.** Gdy to samo słowo pojawia się dwa razy z różnymi
  kontekstami, dzieje się tak dlatego, że oba muszą zostać przetłumaczone
  inaczej — na przykład „Open" jako przycisk i „Open" jako stan.
