---
description: "T-virkņu ziņojumu ekstrahēšana ar pybabel un tas, kā msgfmt un komplektā iekļautais Babel pārbaudītājs validē katalogus."
---

# Ekstrakcija

Ekstrakcija ir solis, kas savāc no jūsu pirmkoda katru atzīmēto ziņojumu
`.pot` veidnē tulkotājiem — [pamācības](tutorial.md) cikla 3. solis. Šī lapa ir
uzziņa par šo soli: konfigurācija, pielāgoti funkciju nosaukumi, stingrais CI
režīms un pārbaudes, kas pēc tam sargā jūsu katalogus.

Ekstrakcijai vajadzīgs papildinājums `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Darbplūsma { #the-workflow }

Izveidojiet `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Tad lietojiet parastās Babel komandas:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` tiek palaists vienreiz katrai valodai; pēc tam `pybabel update` ielok
katru svaigo veidni esošajos katalogos. Šis atkārtojošais cikls — un tas, ko
tā `fuzzy` ieraksti nozīmē laidienam — ir izstaigāts lapā
[Produkcijā](workflow.md#the-cycle-after-the-first-translation).

`gettext_tstrings` ekstraktors apstrādā arī parastos `_()`, `gettext()` un
`ngettext()` izsaukumus, tāpēc viens attēlojums sedz jauktu kodabāzi. Tas
atpazīst `_()`, četrus standarta gettext nosaukumus, `tr()` / `ntr()`
aizstājvārdus un atliktos `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` nav neobligāts"

    `pybabel extract` savāc tulkotāju komentārus tikai tad, ja padodat
    `-c "Translators:"` — tieši tāpat kā parasto gettext izsaukumu gadījumā.

## Savu funkciju nosaukumu reģistrēšana { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Ini fails dod vienu virkni, TOML attēlojums dod sarakstu, un virknes iekšienē
nosaukumus atdala vai nu atstarpes, vai komati. Visi četri pieraksti darbojas.

Opcijas ir `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` un `npgettext_functions`.

!!! danger "`-k` nesniedzas līdz t-virknei"

    Pielāgots palīgs, tāds kā `mytr(t"…")`, ir jānosauc kādā no augšminētajām
    opcijām. Babel `--keyword` mehānisms nespēj nolasīt t-virknes literāli,
    tāpēc `pybabel extract -k mytr` neatrod neko un nesaka neko — ziņojumu POT
    failā vienkārši nav. `-k` joprojām darbojas parastajiem gettext
    izsaukumiem, kas tiek ekstrahēti līdzās.

    Atbalstīta ir tikai standarta argumentu secība: vispirms ziņojums;
    `pgettext` gadījumā konteksts, tad ziņojums; `npgettext` gadījumā
    konteksts, tad vienskaitlis, tad daudzskaitlis.

## Izturīgs pēc noklusējuma { #robust-by-default }

Viens slikts fails neizbeidz visu izpildi:

- T-virkne, ko ekstraktors noraida — piekļuve atribūtiem, izteiksme, nepareizs
  arguments —, tiek ziņota kā brīdinājums un izlaista.
- Fails, ko neizdodas parsēt, tiek izlaists tāpat.
- Tāpat arī fails, ko atsakās pieņemt tikai `tokenize`, kamēr `ast` to pieņem
  un uz kura paša Babel gājiens citādi pārtrauktu darbu.

Iestatiet attēlojuma opcijās `strict = true`, lai katru no šiem pārvērstu par
smagu kļūmi, un tieši to jūs gribat CI vidē.

## Jūsu esošā rīkkopa validē šos katalogus { #your-existing-toolchain-validates-these-catalogs }

Babel atzīmē katru ekstrahēto ziņojumu ar standarta karogu, un tieši šī viena
rinda aktivizē vietturu pārbaudi rīkos, ko jūs jau tā palaižat:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Iztulkojiet to kā `こんにちは {nombre}`, un kļūda tiek noķerta bez jebkādas
konfigurācijas:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate dokumentē to pašu pārbaudi kā [Python brace format][weblate-checks], un
komerciālajām platformām ir sava vietturu kvalitātes kontrole, kas balstās uz
to pašu karogu. Viņu uzvedība ir viņu ziņā; abi zemāk minētie rīki ir tie, kas
šeit ir pārbaudīti.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Papildus tam pakotne reģistrē Babel **pārbaudītāju**, tāpēc `pybabel compile`
piemēro specifikācijas likumus katram ziņojumam, kas nes `gettext-tstrings`
marķiera komentāru:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Daudzskaitļa ziņojumam norāde nosauc formu, jo Babel ziņotais rindas numurs ir
msgid rindas numurs, bet krievu blokam zem tā ir trīs `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` `.mo` failu tik un tā ieraksta"

    Augstāk redzamā kļūda tiek ziņota, izejas statuss ir `1` — un sabojātais
    katalogs tomēr tiek kompilēts. Tikai šis izejas statuss var neļaut
    konveijeram to piegādāt; [Ko CI aiztur](workflow.md#what-ci-gates) parāda
    būvēšanas soli, kas to izdara.

Abas pārbaudes nav lieks dublējums. Komplektā iekļautais pārbaudītājs vismaz
divās vietās ir stingrākā puse:

- Msgid, kura vienīgās figūriekavas ir atsoļotas (`Config {{raw}} only`), nekad
  nesaņem `python-brace-format` karogu, tāpēc to nevalidē neviens ārējs rīks.
- Daudzskaitļa formas tiek pārbaudītas pa vienai. `msgfmt --check-format`
  nolasa tieši to pašu failu, kas augstāk, un iziet ar `0`; forma, kas nomet
  vietturi, kuru tās māsas patur, tur tiek pieņemta, bet šeit noraidīta.

`msgfmt` pārbauda tikai tos vietturu nosaukumus, ko spēj noparsēt kā Python
brace formātu, tāpēc ASCII nosaukumi ļauj ziņojumu validēt katram ķēdes rīkam.
Pati bibliotēka pieņem jebkuru `str.isidentifier()` nosaukumu.

## Veidnes un citi rīki { #templates-and-other-tools }

T-virknes ir Python sintakse, tāpēc šī bibliotēka sedz Python pirmkodu. Veidņu
valodas turpina lietot savu i18n — Jinja2 `{% trans %}`, Django veidņu tagus —
un Babel ekstraktorus tām. Viss barojas vienā un tajā pašā PO katalogā, tāpēc
viena tulkošanas darbplūsma joprojām sedz jauktu kodabāzi.

`pygettext` šodien nespēj parsēt t-virknes, un tieši tāpēc ekstrakcija notiek
caur Babel. Konvencija ir pierakstīta [specifikācijā](spec.md), lai to varētu
mērķēt cits ekstraktors vai nākotnes `pygettext`.
