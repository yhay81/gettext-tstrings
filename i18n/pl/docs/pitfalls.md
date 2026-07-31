---
description: "Co naprawdę psuje się przy tłumaczeniu jednej małej strony na trzydzieści pięć języków, co z tego biblioteka potrafi wychwycić za ciebie, a czego nie."
---

# Pułapki

Ta strona jest przetłumaczona na trzydzieści pięć języków, a każde z tych
tłumaczeń powstało przez przejście pętli, której uczy ta dokumentacja. Jak na
branżowe standardy to niewielki korpus, a i tak wystarczył, by trafić na
większość pułapek, przez które i18n jest trudniejsze, niż wygląda.

Każdy poniższy rozdział to coś, co naprawdę poszło tu nie tak, jak to wtedy
wyglądało i gdzie przebiega granica między tym, co biblioteka sprawdza za
ciebie, a tym, co pozostaje twoją oceną.

## Zmiana nazwy zmiennej tłumaczy zdanie od nowa { #renaming-a-variable-retranslates-a-sentence }

msgid jest kluczem katalogu, a interpolowana nazwa jest *w jego wnętrzu*.
Przeniesienie jednej stałej do zakresu modułu i zapisanie jej wielkimi
literami, tak jak każe styl Pythona — `author` na `AUTHOR` — zmieniło
`Copyright © 2026 {author} · MIT License` w komunikat, którego żaden katalog
nigdy nie widział. Każde tłumaczenie tej linii przeszłoby ponownie przez cykl
fuzzy, w każdym języku, z powodu zmiany nazwy, która nie zmieniła nic, co
czytelnik mógłby zobaczyć.

Biblioteka cię nie powstrzyma: obie pisownie są poprawnymi nazwami symboli
zastępczych. Robi natomiast to, że czyni tę nazwę *wartą* ochrony —
interpolacja musi być [zwykłą nazwą](internals.md#from-template-to-msgid),
więc to, co trafia do klucza katalogu, jest słowem, które tłumacz może
przeczytać, a nie wyrażeniem.

Przypadek odwrotny jest bezpieczny z założenia. Konwersje i specyfikatory
formatu nie są częścią msgid, więc zaostrzenie `{amount:,.2f}` do
`{amount:,.0f}` nie zmienia żadnego klucza i nie unieważnia nigdzie żadnego
tłumaczenia.

## `nplurals=2` nie oznacza dwóch różnych łańcuchów { #nplurals-2-does-not-mean-two-different-strings }

Turecki, węgierski, perski i bengalski deklarują po dwie formy liczby mnogiej
i we wszystkich czterech obie formy policzalnego komunikatu to zgodnie z
prawidłami *ten sam łańcuch* — rzeczownik po liczebniku zostaje w liczbie
pojedynczej, więc `{n} sayfa` jest poprawne i dla jednej strony, i dla
dziesięciu. Recenzent, który „naprawi" to powtórzenie, psuje tłumaczenie.

Odwrotna pomyłka jest równie łatwa. Trzecia forma łotewskiego istnieje
**wyłącznie dla zera**; druga forma słoweńskiego to **liczba podwójna**, dla
dokładnie dwóch; ostatnia forma rumuńskiego wymaga słowa `de`, którego dwie
pierwsze mieć nie mogą. Wypełnienie tych miejsc liczbą pojedynczą i mnogą daje
katalog błędny tylko dla liczebności, których nikt nie testuje.

Co gorsza, *kolejność* miejsc nie jest semantyczna. Walijski indeksuje swoje
pięć form tak, że `msgstr[0]` to przypadek ogólny, a `msgstr[1]` to liczba
pojedyncza. Wypełnianie ich w oczywistej kolejności umieszcza liczbę
pojedynczą tam, gdzie znajdzie ją każdy niepoliczalny komunikat.

Biblioteka nie bierze niczego z tego na siebie i o to właśnie chodzi: reguła
liczby mnogiej języka docelowego mieszka w nagłówku jego własnego katalogu, a
[reguła sumy/części wspólnej](spec.md) pozwala tłumaczeniu mieć więcej form
niż źródło albo mniej. Sprawdza jedyną rzecz, jaką da się sprawdzić bez
znajomości języka — że każda forma zachowuje potrzebne jej symbole zastępcze.

## Dwie formy mogą być identyczne nie bez powodu { #two-forms-can-be-identical-for-a-reason }

Irlandzki ma pięć form liczby mnogiej i w raporcie z buildu tej strony kilka
z nich zapisanych jest tak samo. To nie wpadka przy kopiuj-wklej:
*leathanach* zaczyna się na `l`, a żadna z dwóch mutacji nagłosowych
wywoływanych przez irlandzkie liczebniki nie jest na `l` zapisywana. Formy
nadal wykonują prawdziwą pracę — temat wymienia się między *leathanach* a
*leathanaigh*, a liczebności powyżej dziesięciu wracają do liczby pojedynczej
— ale żaden rzeczownik o znaczeniu „strona" nie pokazałby tego kontrastu.

Każde sprawdzenie oznaczające zduplikowane formy jako podejrzane oznaczy
poprawny irlandzki. Jedynym recenzentem jest tu człowiek, który zna ten język.

## Komunikat może uzgodnić się tylko z jedną liczbą { #a-message-can-only-agree-with-one-count }

Raport z buildu tej strony mówi, ile stron wyrenderowano i ile to zajęło.
Zapisanie tego jako „Rendered {n} pages in {seconds} seconds" wygląda
niewinnie i nie jest przetłumaczalne: gettext wybiera jedną formę na
podstawie jednej liczby, a tą liczbą jest `n`. Słowo *seconds* musiałoby
uzgodnić się z liczbą, której maszyneria liczby mnogiej nigdy nie widzi.

Rozwiązaniem jest uczynić drugą wielkość symbolem jednostki, a nie słowem — a
symbole jednostek same podlegają lokalizacji: katalogi tej strony niosą `s`,
`с`, `ث`, `שנ׳` i `mp`, a francuska, hiszpańska i szwedzka typografia chce
spacji przed symbolem tam, gdzie angielska nie. Nic z tego nie jest sprawą
biblioteki — ale zauważenie, że komunikat wymaga *dwóch* uzgodnień, już tak, a
jedynym narzędziem do tego jest zapisanie komunikatu inaczej.

## Zmiana angielskiego zdania zmienia obcą gramatykę { #editing-an-english-sentence-edits-foreign-grammar }

Strona główna mówiła kiedyś „all ten language editions". Usunięcie liczby —
jednosłowna angielska poprawka, zrobiona dlatego, że liczba wciąż się
dezaktualizowała — zmieniło podmiot z mnogiego na pojedynczy. Hiszpański,
włoski, portugalski, rosyjski, ukraiński, grecki, niderlandzki i hebrajski
musiały na nowo uzgodnić czasownik; kilka potrzebowało też zmiany imiesłowu.

Zmiana w źródle, która po angielsku czyta się jak drobiazg, nie jest
drobiazgiem dalej w potoku. Oznaczenie jej jako fuzzy, co robi
`pybabel update`, jest mechanizmem dającym każdemu tłumaczowi szansę, by to
zauważył.

## Niewidoczne różnice przeżywają każde kopiuj-wklej { #invisible-differences-survive-every-copy-paste }

Przewodnik cytuje diagnostykę zawierającą `(nаme)` — celową sekwencję
ucieczki, bo znak, który nazywa, to cyrylickie `а`, którego żaden czytelnik
nie odróżni od łacińskiego. Tłumacze tej strony zamienili tę sekwencję
ucieczki na rzeczywisty znak **pięć osobnych razy**, w pięciu różnych
językach, za każdym razem tworząc stronę, która wyglądała poprawnie i była
błędna.

Akurat to biblioteka wychwytuje i to jest powód, dla którego diagnostyka ma
taki kształt: symbol zastępczy, którego litery mieszają systemy pisma, jest
[raportowany dwukrotnie](internals.md#diagnostics-are-part-of-the-design), raz
czytelnie i raz z ucieczką, bo forma z ucieczką jest jedynym zapisem, który je
rozróżnia. Twarda spacja wewnątrz nawiasów klamrowych jest z tego samego
powodu wypisywana punktem kodowym. Checker katalogów odrzuca komunikat, zanim
ten zdąży trafić na produkcję.

## Niepusty to nie przetłumaczony { #non-empty-is-not-translated }

Katalog wygenerowany z msgidami skopiowanymi do msgstrów przechodzi każde
naiwne sprawdzenie: nic nie jest puste, nic nie jest fuzzy, zbiór komunikatów
zgadza się dokładnie. Jedno wydanie tej strony działało tak przez kilka
godzin. Podobnie osiem stron innego wydania, które były kopiami angielskiego
źródła co do bajtu — co przechodzi sprawdzenie porównujące bloki kodu między
nimi, bo to ten sam plik.

Żadnej z tych rzeczy biblioteka tłumaczeń nie jest w stanie zobaczyć. Obie są
tanie do przetestowania, kiedy już się wie, że trzeba: porównaj ze źródłem i
wymagaj różnicy.

## Katalog to nie jedyna przetłumaczona rzecz { #the-catalog-is-not-the-only-translated-thing }

Dwie tutejsze awarie nie miały nic wspólnego z gettextem.

Przetłumaczenie nagłówka zmienia kotwicę z niego generowaną, więc każdy link
międzystronicowy prowadzący do tej sekcji się psuje — po cichu i tylko w tym
języku. Ta strona przypina angielską kotwicę do każdego nagłówka, a test
wyprowadza oczekiwaną listę ze strony angielskiej.

A generator strony dostarcza tłumaczenia interfejsu dla sześćdziesięciu ośmiu
języków, wśród których nie ma suahili ani irlandzkiego. Bez takiego
tłumaczenia build nie degraduje się do angielskiego; include szablonu zawodzi
i wydania w ogóle nie da się zbudować. Dwa własne pliki tego repozytorium
istnieją po to, by wypełnić tę lukę.

## Twoje narzędzia też mają błędy { #your-tools-have-bugs-too }

Krok CI, który ta dokumentacja poleca do wychwytywania nieaktualnych
katalogów, `pybabel update --check`, nie jest w stanie wykonać tego zadania w
żadnym projekcie używającym `pgettext` lub `npgettext`. W Babelu 2.18.0 zgłasza
każdy katalog z `msgctxt` jako nieaktualny, przy każdym uruchomieniu.
Porównanie przechodzi przez `Catalog.is_identical`, które wyszukuje każdy
komunikat po kluczu, pod którym jest przechowywany — a dla komunikatu z
kontekstem tym kluczem jest para `(id, context)`, której `Catalog.get` nie
przyjmuje. Wyszukiwanie nie zwraca nic i katalogi nigdy nie okazują się równe:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Został tu znaleziony przy próbie użycia, zgłoszony do upstreamu, a zastępczy
test znajdziesz [na stronie o produkcji](workflow.md#what-ci-gates).

Ogólna lekcja jest ta niewygodna: bramka, która zawsze świeci na czerwono,
jest gorsza niż jej brak, bo zespół ją wyłącza. Sprawdź, czy twój test CI
naprawdę potrafi przejść, zanim zaufasz mu, że zgłosi błąd.

## Po co jest ta biblioteka, w jednym zdaniu { #what-the-library-is-for-in-one-line }

Większość tej strony to oceny, których żadne narzędzie nie przejmie. To, co
narzędzie *potrafi*, to zagwarantować, że tłumaczenie nie może zmienić
struktury zdania, które tłumaczy — nie może pominąć wartości, wymyślić jej,
przeformatować ani sięgnąć do twoich obiektów — i powiedzieć o tym zdaniem, na
podstawie którego osoba mająca to naprawić może działać. To całość tego, co ta
biblioteka obiecuje, a reszta tej strony to sposób, w jaki tego dotrzymuje.
